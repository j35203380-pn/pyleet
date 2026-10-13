from app.auth.service.database import DbService
from app.auth.schemas.token import SessionAddDTO,TokenCacheDTO,SessionUpdDTO,TokenCreateDTO
from app.auth.schemas.database import UserAuthAdd, UserTOTPDTO,UserLoginGetDto
from app.auth.schemas.auth import PayloadDTO,TokenTypeEN,PayloadGetEN
from app.auth.service.token import TokenService
from app.auth.service.utils import JwtService
from app.auth.service.crypto import CryptoService
from app.auth.service.totp_2fa import UserTotpService
from app.exceptions import UserTokenError
import hashlib, asyncio, logging




class UserAuthService:
    def __init__(self,repo: DbService, 
                 jwt_: JwtService,
                 crypt_: CryptoService,
                 token_: TokenService,
                 totp_: UserTotpService):
        self._db=repo
        self._jwt=jwt_
        self._crypt=crypt_
        self._token=token_
        self._totp=totp_


    
    async def add_user(self,users: UserAuthAdd):
        logging.info('запрос принят')
       
        password_hash=await self._crypt.hash_password(password=users.password)
        
        us=dict(
            name=users.name,
            nik_name=users.nik_name,
            email=users.email,
            password=password_hash
            )
        await self._db.user_add(us)
    
    
    
    async def __token_user__(self,user_id,nik_name):
        token_access= self._jwt.create_token(PayloadDTO(user_id=user_id,token_type=TokenTypeEN.ACCESS,nik_name=nik_name))
        token_refresh= self._jwt.create_token(PayloadDTO(user_id=user_id,token_type=TokenTypeEN.REFRESH,nik_name=nik_name))
        token=await asyncio.gather(token_access,token_refresh)
        return token



    async def __add_token__(self,token_hash,sess):
    
        add_ses=self._db.session_add(sessions=sess)
        token_ses=self._token.set_token(token_hash=token_hash,refresh=TokenCacheDTO())
        try:
                
            async with asyncio.TaskGroup() as ts:
                ts.create_task(add_ses)
                ts.create_task(token_ses)
        except* Exception as ex:

            for e in ex.exceptions:
                logging.error("ошибка в TaskGroup: %r", e, exc_info=e)
            raise
    
    
    async def _tokens_create_db_(self,user: TokenCreateDTO): 

        token=await self.__token_user__(user.user_id,user.nik_name)
        access_,refresh_=token

        token_hash=hashlib.sha256(refresh_.encode()).digest()
        
        sess=SessionAddDTO(user_id=user.user_id,user_agent=user.user_agent,
                        ip_adress=user.ip_adress,token_hash=token_hash)

        
        await self.__add_token__(token_hash,sess)
        return access_,refresh_
    
    
    
    async def login_user(self,username: str, password: str,ip_adress: str, user_agent: str):
        
        user: UserLoginGetDto=await self._db.user_login(username=username)
        if user.is_error:
            
            await self._crypt.verify_password(hash=user.passsword_hash,password=password)
            raise user.is_error()
        
        await self._crypt.verify_password(hash=user.passsword_hash,password=password)
        
       
        tok_cr=TokenCreateDTO(user_id=user.user_id,nik_name=user.nik_name,
                              ip_adress=ip_adress,user_agent=user_agent)
        
        return await self._tokens_create_db_(tok_cr)





    async def login_user_2fa(self,username: str, password: str):
        
        user: UserLoginGetDto=await self._db.user_login(username=username)
        if user.is_error:
            
            await self._crypt.verify_password(hash=user.passsword_hash,password=password)
            raise user.is_error()
        
        await self._crypt.verify_password(hash=user.passsword_hash,password=password)
        
        if  user.is_totp_enable:
            two_code=await self._totp.get_totp_user(user.user_id)
            token_2fa=await self._jwt.create_token(PayloadDTO(
                                                    user.user_id,
                                                    user.nik_name,
                                                    token_type=TokenTypeEN.TWO_FACT))
            return {'2fa': two_code, 'token': token_2fa}
        
        raise ValueError( "У вас нет двухфакторной аутенфикации")




    async def __del_token__(self,token_hash):
        token_base=self._db.del_token(token_hash)
        token_cache=self._token.del_token(token_hash)
        await asyncio.gather(token_cache,token_base)
        raise UserTokenError()

    
    



    async def refresh_user_tokens(self, refresh_tn: str,ip_adress: str,user_agent: str|None=None):
        
        token=await self._jwt.refresh_token(refresh_tn)
        token_hash=hashlib.sha256(refresh_tn.encode()).digest()
        cache_token=await self._token.get_tokens(token_hash)
        if cache_token=='VZLOM': 
            await self.__del_token__(token_hash)

        elif not cache_token:
            await self._db.session_validate_tokens(token_hash)
              
        user_id,nik_name=token[PayloadGetEN.ID],token[PayloadGetEN.NIK_NAME]
        
        access_new,refresh_new=await self.__token_user__(user_id,nik_name)

        new_token_hash=hashlib.sha256(refresh_new.encode()).digest()
        
        new_ses=SessionUpdDTO(token_hash=new_token_hash,
                            ip_adress=ip_adress,
                            user_agent=user_agent)
        
        delete_token= self._token.del_token(token_hash)
        session_upd= self._db.session_update_token(token_hash=token_hash,sess=new_ses)
        add_token=self._token.set_token(token_hash=new_token_hash,refresh=TokenCacheDTO())
        try:
                
            async with asyncio.TaskGroup() as ts:
                ts.create_task(delete_token)
                ts.create_task(session_upd)
                ts.create_task(add_token)
        except* Exception as ex:
            raise ValueError(ex)
        return access_new,refresh_new
        
        

    async def totp_user2fa_create(self,user_id):
        'Подключение 2FA'
        return await self._totp.create_totp(UserTOTPDTO(user_id=user_id))


    async def totp_add_2fa_code(self, code: str,user_id):
        'Подтверждение кода для подключения 2FA '
        return await self._totp.add_totp(code,user_id)


    async def totp_login_verify_code(self,code: str,nik_name: str, user_id,user_agent: str,ip_adress: str,token: str):
        'Для входа в аккаунт'
        await self._totp.totp_verify_user(code=code,user_id=user_id)
        user_cr=TokenCreateDTO(user_id=user_id,nik_name=nik_name,
                               ip_adress=ip_adress,user_agent=user_agent)
        await self._jwt.logout(token)
        return await self._tokens_create_db_(user_cr)
         

        
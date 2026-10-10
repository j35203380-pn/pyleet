from app.auth.service.database import DbService
from app.auth.schemas.token import SessionAddDTO,TokenCacheDTO,SessionUpdDTO
from app.auth.schemas.database import UserAuthAdd
from app.auth.schemas.auth import PayloadDTO,TokenTypeEN,PayloadGetEN
from app.auth.service.token import TokenService
from app.auth.service.utils import JwtService
from app.auth.service.crypto import CryptoService
from app.exceptions import UserTokenError
import hashlib, asyncio, logging




class UserAuthService:
    def __init__(self,repo: DbService, 
                 jwt_: JwtService,
                 crypt_: CryptoService,
                 token_: TokenService):
        self._db=repo
        self._jwt=jwt_
        self._crypt=crypt_
        self._token=token_

    
    async def add_user(self,users: UserAuthAdd):
        logging.info('запрос принят')
       
        password_hash=await self._crypt.hash_password(password=users.password)
        
        us=dict(
            name=users.name,
            nik_name=users.nik_name,
            email=users.email,
            password=password_hash
            )
    
    
    
    async def _token_user_(self,user_id,nik_name):
        token_access= self._jwt.create_token(PayloadDTO(user_id=user_id,token_type=TokenTypeEN.ACCESS,nik_name=nik_name))
        token_refresh= self._jwt.create_token(PayloadDTO(user_id=user_id,token_type=TokenTypeEN.REFRESH,nik_name=nik_name))
        token=await asyncio.gather(token_access,token_refresh)
        return token



    async def __add_token__(self,token_hash,sess):
    
        add_ses=self._db.session_add(sessions=sess)
        token_ses=self._token.set_token(token_hash=token_hash,refresh=TokenCacheDTO())
        
        async with asyncio.TaskGroup() as ts:
            task=ts.create_task(add_ses())
            task=ts.create_task(token_ses())



    async def get_user(self,username: str, password: str,ip_adress: str, user_agent: str):
        
        user=await self._db.user_login(username=username)

        user_id,nik_name,hash_password=user.id, user.nik_name, user.password
        await self._crypt.verify_password(hash=hash_password,password=password)
      
        token=await self._token_user_(user_id,nik_name)
        access_,refresh_=token

        token_hash=hashlib.sha256(refresh_.encode()).digest()
        
        sess=SessionAddDTO(user_id=user_id,user_agent=user_agent,
                        ip=ip_adress,token_hash=token_hash)

        
        await self.__add_token__(token_hash,sess)
        return access_,refresh_



    async def __del_token__(self,token_hash):
        token_base=self._db.del_token(token_hash)
        token_cache=self._token.del_token(token_hash)
        await asyncio.gather(token_cache,token_base)
        raise UserTokenError()

    
    

    async def refresh_user_tokens(self, refresh_tn: str,ip_adress: str,user_agent: str|None=None):
        
        token=await self._jwt.current_token(refresh_tn)
        token_hash=hashlib.sha256(refresh_tn.encode()).digest()
        cache_token=await self._token.get_tokens(token_hash)
        if cache_token=='VZLOM': 
            await self.__del_token__(token_hash)

        elif not cache_token:
            await self._db.session_validate_tokens(token_hash)


        user_id,nik_name=token[PayloadGetEN.ID],token[PayloadGetEN.NIK_NAME]
        
        access_new,refresh_new=await self._token_user_(user_id,nik_name)

        new_token_hash=hashlib.sha256(refresh_new.encode()).digest()
        
        new_ses=SessionUpdDTO(token_hash=new_token_hash,
                            ip_adress=ip_adress,
                            user_agent=user_agent)
        
        delete_token= self._token.del_token(token_hash)
        session_upd= self._db.session_update_token(token_hash=token_hash,sess=new_ses)
        add_token=self._token.set_token(token_hash=new_token_hash,refresh=TokenCacheDTO())

        async with asyncio.TaskGroup() as ts:
            ts.create_task(delete_token)
            ts.create_task(session_upd)
            ts.create_task(add_token)

        return access_new,refresh_new
        
        





import qrcode,pyotp,io,time
from app.auth.repositories.db import AuthRepositories
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.settings.base import secret_totp
from app.auth.schemas.database import UserTOTPDTO
from app.database.models import UserTOTP
from cryptography.fernet import Fernet
from app.exceptions import TotpNotFound,TotpConflictUser,TotpErrorCode,TotpLockedUntil,TotpErrorUsedTime
from datetime import datetime,timedelta,timezone
from uuid import UUID




class UserTotpService:

    def __init__(self,repo_auth: AuthRepositories,db:AsyncSession):
        self._db=db
        self._repo=repo_auth
    MAX_ATTEMPTS=5
    LOCK_TIME=timedelta(minutes=5)
    fern=Fernet(secret_totp.get_secret_value())

    async def create_totp(self,user: UserTOTPDTO):
        
        SECRET=pyotp.random_base32()
        enc_secret=self.fern.encrypt(SECRET.encode())
        user_totp=dict(user_id=user.user_id,
                                 secret=enc_secret,
                                 last_used_step=user.last_used)
        async with self._db.begin():
            await self._repo.insert_totp(user_totp)

            buf=io.BytesIO()
            totp=pyotp.TOTP(SECRET)
            provisioning_uri=totp.provisioning_uri(name=str(user.user_id),issuer_name='pyleet')
            qrcode.make(provisioning_uri).save(buf,format='PNG')

        return dict(qr=buf.getvalue(),format='image/png',code=totp.now())


    
    async def add_totp(self,code: str,user_id: UUID):
        timecode=int(time.time()/30)
        err_totp=False
        async with self._db.begin():
            row: UserTOTP= await self._repo.select_totp(user_id)

            if not row:
                raise TotpNotFound()

            elif row.enable:
                raise TotpConflictUser()

            elif row.locked_until and row.locked_until>datetime.now(timezone.utc):
                raise TotpLockedUntil


            secret=self.fern.decrypt(row.secret).decode()
            
            if not pyotp.TOTP(secret).verify(otp=code,valid_window=1):
                row.failed_attempts+=1
                p=self.MAX_ATTEMPTS- row.failed_attempts
                if row.failed_attempts>=self.MAX_ATTEMPTS:
                    row.locked_until=datetime.now(timezone.utc)+self.LOCK_TIME
                    row.failed_attempts=0
                    err_totp=TotpLockedUntil
                else:
                    err_totp=TotpErrorCode

            else:
                row.locked_until=None
                row.enable=True
                row.last_used_step=timecode
                row.failed_attempts=0
                return "Аутенфикация прошла успешно!"

        if err_totp:
            raise err_totp()



    async def totp_verify_user(self,code: str, user_id: UUID):
        err=False
        async with self._db.begin():
            totp: UserTOTP=await self._repo.select_totp(user_id)
          
            if totp.locked_until and  totp.locked_until> datetime.now(timezone.utc):
                raise TotpLockedUntil()

            elif totp.last_used_step ==int(time.time()//30):
                raise TotpErrorUsedTime()

            secret=self.fern.decrypt(totp.secret).decode()

            if not pyotp.TOTP(secret.encode()).verify(code,valid_window=1):
                totp.failed_attempts+=1
                if totp.failed_attempts>=self.MAX_ATTEMPTS:
                    totp.locked_until=datetime.now(timezone.utc)+self.LOCK_TIME
                    totp.failed_attempts=0
                    err=TotpLockedUntil
                else:
                    err=TotpErrorCode

            else:
                print('авутенфикация прошлав успешно!')
                totp.last_used_step=int(time.time())
                totp.locked_until=None
                totp.failed_attempts=0
                return f'Аутенфикация прошла успешно!'

        if err:
            raise err()


    async def get_totp_user(self,user_id: UUID):
        async with self._db.begin():
            totp: UserTOTP=await self._repo.select_totp(user_id)

            if not totp:
                raise TotpNotFound()

            elif not totp.enable:
                raise TotpNotFound()

            elif totp.locked_until and  totp.locked_until> datetime.now(timezone.utc):
                raise TotpLockedUntil()

            elif totp.last_used_step ==int(time.time()//30):
                raise TotpErrorUsedTime()

            buf=io.BytesIO()
            secret=self.fern.decrypt(totp.secret).decode()
            code=pyotp.TOTP(secret)
            provision_url=code.provisioning_uri(str(user_id),issuer_name='pyleet')
            qrcode.make(provision_url).save(buf,format='PNG')
        
        return dict(qr=buf.getvalue(),format='image/png',code=code.now())
        

            
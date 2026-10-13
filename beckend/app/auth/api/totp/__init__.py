from app.auth.api.totp.totp_auth import router as auth_2fa
from app.auth.api.totp.totp_login import router as login_2fa
from fastapi import APIRouter


router=APIRouter(prefix='/2fa')

router.include_router(auth_2fa)
router.include_router(login_2fa)
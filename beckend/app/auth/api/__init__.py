from fastapi import APIRouter
from app.auth.api.auth import router as auth_rout
from app.auth.api.login import router as login_rout

router=APIRouter(prefix='/auth',tags=["Авторизация и Вход"])

router.include_router(auth_rout)
router.include_router(login_rout)
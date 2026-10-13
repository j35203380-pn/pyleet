from fastapi import APIRouter,Depends,Response
from app.auth.dependcies.auth import current_token,AuthService




router=APIRouter(tags=['Добавить 2FA'])


@router.post('/setup/qr')
async def create_2fa(us: AuthService,token=Depends(current_token)):
    id=token['id']
    compect: dict= await us.totp_user2fa_create(id)

    return Response(content=compect['qr'], media_type=compect['format'])




@router.post('/setup/code')
async def create_2fa(us: AuthService,token=Depends(current_token)):
    id=token['id']
    compect: dict= await us.totp_user2fa_create(id)

    return compect['code']






@router.post('/setup/verify')
async def add_code_2fa(code: str, us: AuthService,token=Depends(current_token)):
    id=token['id']
    data=await us.totp_add_2fa_code(code=code,user_id=id)
    return data

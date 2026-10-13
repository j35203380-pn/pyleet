from fastapi import APIRouter,Request,Response,Cookie,Depends
from app.auth.dependcies.auth import AuthService,UsReqForm,current_2fa_token
from app.auth.settings.base import expire



router=APIRouter(tags=['Верификация'])



@router.post('/login/code')
async def login_2fa(user: UsReqForm,serv: AuthService):
    
    data=await serv.login_user_2fa(user.username,user.password)
    code=data['2fa']['code']
    return {'access': data['token'], 
            'token_type': 'bearer',
              'code': code,
              'headers': 'подтвердите вход'} 



@router.post('/code')
async def get_code_2fa(code : str, serv: AuthService,request: Request,response: Response,token=Depends(current_2fa_token)):
    ip_adr=request.client.host
    user_ag=request.headers.get('user_agent')
    user_id,nik_name=token['id'],token['nik_name']
    
    data=await serv.totp_login_verify_code(code,nik_name,
                                           user_id,
                                           user_agent=user_ag,
                                           ip_adress=ip_adr,
                                           token=token)
    access,refresh=data

    response.set_cookie(
        key='refresh_token',
        value=refresh,
        secure=True,
        httponly=True,
        samesite='lax',
        max_age=expire.refresh_exp
    )

    return {'access': access, 'token_type': 'bearer'}

    

    
    


from fastapi import APIRouter,Request,Response,Cookie
from app.auth.dependcies.auth import AuthServ,UsReqForm
from app.auth.settings.base import expire



router=APIRouter()



@router.post('/login')
async def login(user: UsReqForm,serv: AuthServ,request: Request,response: Response):
    ip_adress=request.client.host
    user_agent=request.headers.get("user_agent")
    token=await serv.get_user(username=user.username,password=user.password,
                                user_agent=user_agent,ip_adress=ip_adress)
    access,refresh=token


    response.set_cookie(
        key='refresh_token',
        value=refresh,httponly=True,
        secure=True,samesite="lax",max_age=expire.refresh_exp
    )

    
    return {'access_token' : access, 'token_type': 'bearer'} 





@router.put('/refresh')
async def refresh_token(request: Request,response: Response,serv: AuthServ,
                                            refresh_token:str|None=Cookie()):

    ip_adress=request.client.host
    user_agent=response.headers.get['user_agent']
    access,refresh=await serv.refresh_user_tokens(refresh_token,ip_adress,user_agent)

    response.set_cookie(
        key='refresh_token',
        value=refresh,httponly=True,
        secure=True,samesite="lax",max_age=expire.refresh_exp
    )

    return {'access_token' : access, 'token_type': 'bearer'} 

    
    


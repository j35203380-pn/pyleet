from app.routers.sellers.update_task import routers as routers_task
from app.routers.coments_user import routers as routers_comment
from fastapi import APIRouter

approuter=APIRouter()

approuter.include_router(routers_task)
approuter.include_router(routers_comment)


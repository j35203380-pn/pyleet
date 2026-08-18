from app.routers.sellers.update_task import routers
from fastapi import APIRouter

approuter=APIRouter()

approuter.include_router(routers)


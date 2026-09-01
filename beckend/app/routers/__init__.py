from beckend.app.routers.solution_router import router as router_solution
from app.routers.coments_user import routers as routers_comment
from fastapi import APIRouter

approuter=APIRouter()

approuter.include_router(router_solution)
approuter.include_router(routers_comment)


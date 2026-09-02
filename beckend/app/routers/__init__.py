from app.routers.solution_router import router as router_solution
from app.routers.coments_user import routers as routers_comment
from app.routers.get_task import routers as routers_task
from app.routers.category_task import routers as routers_category
from fastapi import APIRouter

approuter=APIRouter()

approuter.include_router(router_solution)
approuter.include_router(routers_comment)
approuter.include_router(routers_task)
approuter.include_router(routers_category)

from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.veiculos import router as veiculos_router

api_router = APIRouter()
router_list = [auth_router, veiculos_router]

for router in router_list:
    api_router.include_router(router)
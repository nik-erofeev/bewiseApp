"""Корневой роутер приложения"""

from fastapi import APIRouter

from app.api.application.router import router as application_router
from app.core.settings import APP_CONFIG

router = APIRouter(
    prefix=f"{APP_CONFIG.api.v1}",
)


routers = (application_router,)
for resource_router in routers:
    router.include_router(resource_router)

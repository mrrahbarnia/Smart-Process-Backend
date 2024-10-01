import logging
from logging.config import dictConfig

from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import LogConfig, app_configs
from src.auth import router as auth_router
from src.admin import router as admin_router
from src.products import router as products_router
from src.cart import router as cart_router

logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    dictConfig(LogConfig().model_dump())
    logger.info("App is running...")
    yield


app = FastAPI(**app_configs, lifespan=lifespan)

origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(router=auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(router=admin_router.router, prefix="/admin", tags=["admin"])
app.include_router(router=products_router.router, prefix="/products", tags=["products"])
app.include_router(router=cart_router.router, prefix="/cart", tags=["cart"])

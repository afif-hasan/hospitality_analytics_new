from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import register_exception_handlers

from app.modules.auth.controller import router as auth_router
from app.modules.transactions.controller import router as transactions_router
from app.modules.analytics.controller import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(debug=settings.DEBUG)
    await init_db()
    yield


app = FastAPI(
    title="Hospitality Analytics API",
    description="Backend service for hospitality transaction data and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
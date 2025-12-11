from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import operators, sources, contacts, leads, stats
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.include_router(operators.router, prefix=settings.API_V1_PREFIX)
app.include_router(sources.router, prefix=settings.API_V1_PREFIX)
app.include_router(contacts.router, prefix=settings.API_V1_PREFIX)
app.include_router(leads.router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Корневой эндпоинт"""
    docs_path = f"{settings.API_V1_PREFIX}/docs" if settings.API_V1_PREFIX else "/docs"
    return {
        "message": settings.APP_NAME + " API",
        "docs": docs_path
    }

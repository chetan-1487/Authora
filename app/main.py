from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api.v1.auth.endpoints import router as auth_router
from .api.v1.user.endpoints import router as user_router
from .api.v1.category.endpoints import router as category_router
from .api.v1.product.endpoints import router as product_router
from .db.base import Base
from .db.session import async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # App runs here


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Project is running"}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_app.core.database import sessionmanager
from fastapi_app.core.middlewares import middleware
from .routers import event_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan, middleware=middleware)
app.include_router(event_manager.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}



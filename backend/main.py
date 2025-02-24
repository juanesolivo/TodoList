from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Conectar MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de dato

# Registrar rutas
app.include_router(auth_router, prefix="/auth")
app.include_router(tasks_router, prefix="/tasks")

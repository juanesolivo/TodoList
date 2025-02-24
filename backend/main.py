from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Conectar con MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de dato

# Registrar rutas
app.include_router(auth_router, prefix="/auth")
app.include_router(tasks_router, prefix="/tasks")

# Configurar seguridad para Swagger
###

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TodoList API",
        version="1.0.0",
        description="API para gestionar una lista de tareas",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

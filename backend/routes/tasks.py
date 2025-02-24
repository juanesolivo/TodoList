from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.task import Task
from config import MONGO_URL
from utils.security import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Conectar con MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de datos
taskcollection = db.tasks  # Colección (tabla)

# Obtener todas las tareas
@router.get("/")
async def get_tasks():
    tasks = await taskcollection.find().to_list(length=None)
    for task in tasks:
        task["id"] = str(task["_id"])
        del task["_id"]
    return tasks

# Crear una nueva tarea
@router.post("/")
async def create_task(task: Task, current_user: dict = Depends(get_current_user)):
    task_dict = task.dict()
    task_dict["created_by"] = current_user["email"]
    new_task = await taskcollection.insert_one(task_dict)
    return {"message": "Tarea creada", "task_id": str(new_task.inserted_id)}

# Actualizar una tarea
@router.put("/{task_id}")
async def update_task(task_id: str, updated_task: Task):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID de tarea no válido")
    
    result = await taskcollection.update_one(
        {"_id": ObjectId(task_id)}, {"$set": updated_task.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return {"message": "Tarea actualizada"}

# Eliminar una tarea
@router.delete("/{task_id}")
async def delete_task(task_id: str):
    result = await taskcollection.delete_one({"_id": ObjectId(task_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return {"message": "Tarea eliminada"}

@router.get("/debug-token")
async def debug_token(token: str = Depends(oauth2_scheme)):
    return {"token": token}
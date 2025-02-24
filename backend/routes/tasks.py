from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.task import Task
from config import MONGO_URL
from utils.security import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Conectar MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de datos
taskcollection = db.tasks  # Coleccion (tabla)

# Obtener todas las tareas del usuario autenticado
@router.get("/")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    tasks = await taskcollection.find({"created_by": user_email}).to_list(length=None)
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

# Actualizar una tarea (solo si es el creador)
@router.put("/{task_id}")
async def update_task(task_id: str, updated_task: Task, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID de tarea no válido")
    
    task = await taskcollection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    if task.get("created_by") != current_user["email"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar esta tarea")
    
    # Extraer datos de actualización y forzar 'created_by'
    updated_data = updated_task.dict()
    updated_data.pop("created_by", None)  # Eliminar si viene en el body
    updated_data["created_by"] = current_user["email"]
    
    result = await taskcollection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updated_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return {"message": "Tarea actualizada"}

# Eliminar una tarea (solo si es el creador)
@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="ID de tarea no válido")
    
    task = await taskcollection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    if task.get("created_by") != current_user["email"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta tarea")
    
    result = await taskcollection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return {"message": "Tarea eliminada"}
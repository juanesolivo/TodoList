from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import User
from utils.security import hash_password, verify_password, create_jwt
from config import MONGO_URL

router = APIRouter()

# Conectar MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de datos
usercollection = db.users  # Colección (tabla)

# Registro de usuario
@router.post("/signup/")
async def signup(user: User):
    # Verificar si el email ya existe
    existing_user = await usercollection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Hashear la contraseña antes de guardarla
    hashed_password = hash_password(user.password)
    
    # Guardar usuario en la base de datos
    user_dict = {"name": user.name, "email": user.email, "password": hashed_password}
    new_user = await usercollection.insert_one(user_dict)
    
    return {"message": "Usuario registrado", "user_id": str(new_user.inserted_id)}

# Iniciar sesión
@router.post("/login/")
async def login(user: User):
    # Buscar usuario por email
    existing_user = await usercollection.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    # Verificar contraseña
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    # Generar token JWT
    token = create_jwt(existing_user["email"])
    
    return {"message": "Inicio de sesión exitoso", "token": token}
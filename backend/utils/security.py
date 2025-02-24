import bcrypt
import jwt
import datetime
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from config import SECRET_KEY
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# Conectar MongoDB (local)
client = AsyncIOMotorClient(MONGO_URL)
db = client.todolist_db  # Base de datos
usercollection = db.users  # Colección (tabla)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hashear la contraseña 
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

# Verificar la contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Generar token JWT
def create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Obtener usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = await usercollection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido")
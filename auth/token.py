from datetime import timedelta, datetime

from fastapi import HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sql import crud, schemes
from sql.database import SessionLocal
from jose import jwt, JWTError
from os import getenv
from dotenv import load_dotenv
from .hash import verify_password

token_router = APIRouter(
    prefix="",
    tags=["Token"],
    responses={404: {"description": "Not found"}},
)

# Cargar variables de enterno.
load_dotenv()

# Variables de entorno.
SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES = getenv("ACCESS_TOKEN_EXPIRES")

# Ruta donde se mandará username y password.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar que el usuario existe.
def get_user(username: str, db: Session = Depends(get_db)):
    
    admin = crud.get_admin_by_username(db=db, username=username)
    professor = crud.get_professor_by_username(db=db, username=username)
    student = crud.get_student_by_username(db=db, username=username)
    
    if admin:
        return admin
    elif professor:
        return professor
    elif student:
        return student
    
    return False
    
# Función para autenticar el username y password del usuario.
def authenticate_user(username, password, db: Session = Depends(get_db)):
    
    user = get_user(username=username, db=db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(plane_password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

# Función para crear el token.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=2)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# Ruta que recibe y verifica la data, y retorna un token de acceso.
@token_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    
    user = authenticate_user(form_data.username, form_data.password, db=db)
    
    access_token_expires = timedelta(days=int(ACCESS_TOKEN_EXPIRES))
    access_token = create_access_token(
        data={"username": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Función de la que dependerán las rutas protegidas, y devolverá la decodificación del token.
def get_current_user(token: str = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        
    except JWTError:
        return credentials_exception
    
    return payload

def validate_username(username: str, db: Session):
    
    admin = crud.get_admin_by_username(db=db, username=username)
    student = crud.get_student_by_username(db=db, username=username)
    professor = crud.get_professor_by_username(db=db, username=username)
    
    if admin or student or professor:
        
        return True
    
    return False
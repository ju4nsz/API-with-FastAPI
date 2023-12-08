from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.token import token_router
from sql import models
from sql.database import engine
from apirouters.apistudent import student_router
from apirouters.apiprofessor import professor_router
from apirouters.apiadmin import admin_router
from config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = settings.origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.include_router(router=token_router)
app.include_router(router=student_router)
app.include_router(router=professor_router)
app.include_router(router=admin_router)
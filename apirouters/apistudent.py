from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session
from sql import schemes, models, crud
from auth.token import get_db, get_current_user, validate_username, verify_password
from fastapi.exceptions import ResponseValidationError

student_router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not found"}},
)

# Ruta para obtener un estudiante '/student/get-student'
@student_router.get("/get-student", response_model=schemes.Student)
def get_student(student = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not student["role"] == "student":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a student.",
        )
    
    try:
        student = crud.get_student_by_username(db=db, username=student["username"])
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity Error")
    except DataError:
        raise HTTPException(status_code=400, detail="Data Error")
    
    return student

# Ruta para obtener los cursos de un estudiante '/student/get-courses/
@student_router.get("/get-courses", response_model=List[schemes.CourseResponse] | None)
def get_courses(student = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not student["role"] == "student":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a student.",
        )
        
    try:
        inscriptions = crud.get_course_info_of_student(db=db, student_username=student["username"])
    except DataError:
        raise HTTPException(status_code=400, detail="Data Error")
    
    return inscriptions

# Ruta para inscribirse a un curso '/student/inscribe-course'
@student_router.post("/inscribe-course", response_model=schemes.InscriptionCreate)
def get_courses(course_id: int,
                password: str,
                student = Depends(get_current_user),
                db: Session = Depends(get_db)
                ):
    
    if not student["role"] == "student":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a student.",
        )
        
    course = crud.get_course_by_id(db=db, course_id=course_id)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    if not verify_password(plane_password=password, hashed_password=course.password):
        
        raise HTTPException(
            status_code=409,
            detail="Invalid password.",
        )
    
    if crud.verify_inscription_of_student(db=db, course_name=course.name, student_username=student["username"]):
        
        raise HTTPException(
            status_code=409,
            detail="You are already enrolled in this course.",
        )
        
    db_student = crud.get_student_by_username(db=db, username=student["username"])
    
    inscription = schemes.InscriptionCreate(
        student_id=db_student.student_id,
        course_id=course_id
    )
    
    try:
        
        db_inscription = crud.create_inscription(db=db, inscription=inscription)
    
    except IntegrityError as e:
        
        error_message = str(e)
        
        if "Duplicate entry" in error_message:
            raise HTTPException(status_code=400, detail="Duplicate Entry")
        
        else:
            raise HTTPException(status_code=400, detail="Integrity error")
        
    return db_inscription
    

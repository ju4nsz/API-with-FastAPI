from fastapi import APIRouter, Depends, HTTPException
from sql import schemes, crud
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from auth.token import get_current_user, get_db, validate_username, verify_password
from typing import List

professor_router = APIRouter(
    prefix="/professor",
    tags=["Professor"],
    responses={404: {"description": "Not found"}},
)

# Ruta para obtener el profesor '/professor/get-professor'
@professor_router.get("/get-professor", response_model=schemes.Professor)    
def get_professor(professor = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not professor["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    try:
        professor = crud.get_professor_by_username(db=db, username=professor["username"])
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity Error")
    except DataError:
        raise HTTPException(status_code=400, detail="Data Error")
    
    return professor

# Ruta para obtener los cursos del profesor '/professor/get-courses'
@professor_router.get("/get-courses", response_model=List[schemes.Course] | None)
def get_courses_of_professor(professor = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not professor["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    db_professor = crud.get_professor_by_username(db=db, username=professor["username"])
    
    try:
        courses = crud.get_courses_of_professor(db=db, professor_username=db_professor.username)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity Error")
    except DataError:
        raise HTTPException(status_code=400, detail="Data Error")
    
    return courses

# Ruta para obtener los estudiantes de un curso '/professor/get-students-of-course'
@professor_router.get("/get-students-of-course", response_model=List[schemes.StudentResponse])
def get_students_of_course(course_name: str, payload: dict = Depends(get_current_user), 
                           db: Session = Depends(get_db)):
    
    if not payload["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    professor = crud.get_professor_by_username(db=db, username=payload["username"])
    
    course = crud.get_course_by_name(db=db, course_name=course_name)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
    
    if not course.professor_id == professor.professor_id:
        
        raise HTTPException(
            status_code=403,
            detail="This is not your course, you can't see the students.",
        )
        
    try:
        
        students = crud.get_students_of_course_by_name(db=db, course_name=course_name)
        
    except IntegrityError:
        
       raise HTTPException(status_code=400, detail="Integrity error")
   
    return students

# Ruta para inscribir a un estudiante en su curso '/professor/inscribe-student'
@professor_router.post("/inscribe-student", response_model=schemes.InscriptionCreate)
def inscribe_student(inscription: schemes.InscriptionCreate,
                     professor = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    
    if not professor["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    student = crud.get_student_by_id(db=db, student_id=inscription.student_id)
    
    if not student:
        
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )
        
    course = crud.get_course_by_id(db=db, course_id=inscription.course_id)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    db_professor = crud.get_professor_by_username(db=db, username=professor["username"])
    
    if not course.professor_id == db_professor.professor_id:
        
        raise HTTPException(
            status_code=403,
            detail="This is not your course, you can't inscribe a student.",
        )
        
    
    if crud.verify_inscription_of_student(db=db, course_name=course.name, student_username=student.username):
        
        raise HTTPException(
            status_code=409,
            detail="The student is already enrolled in the course.",
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

# Ruta para crear un curso '/professor/create-course'
@professor_router.post("/create-course", response_model=schemes.CourseCreate)
def create_course(course: schemes.CourseCreate,
                  professor = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    
    if not professor["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    db_course = crud.get_course_by_name(db=db, course_name=course.name)
    
    if db_course:
        
        raise HTTPException(
        status_code=409,
        detail="Name already exists.",
        )
    
    db_professor = crud.get_professor_by_id(db=db, professor_id=course.professor_id)
    
    if not db_professor:
        
        raise HTTPException(
        status_code=404,
        detail="Professor ID not found.",
        )
        
    db_professor = crud.get_professor_by_username(db=db, username=professor["username"])
    
    if not course.professor_id == db_professor.professor_id:
        
        raise HTTPException(
        status_code=403,
        detail=f"The ID '{course.professor_id}' is not your ID.",
        )
        
    try:
        db_course = crud.create_course(db=db, course=course)
    
    except IntegrityError as e:
        
        raise HTTPException(status_code=400, detail="Integrity error")
        
    return db_course

# Ruta para cambiar la contraseña de un curso '/professor/update-password-of-course' 
@professor_router.put("/update-password-of-course", response_model=dict)
def update_course_password(course_name: str,
                        password: str,
                        update_password: str,
                        payload: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    
    if not payload["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    course = crud.get_course_by_name(db=db, course_name=course_name)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    professor = crud.get_professor_by_username(db=db, username=payload["username"])
    
    if not course.professor_id == professor.professor_id:
        
        raise HTTPException(
            status_code=403,
            detail="This is not your course.",
        )
    
    if not verify_password(plane_password=password, hashed_password=course.password):
        
        raise HTTPException(
            status_code=409,
            detail="Incorrect password of the course.",
        )
        
    try:
        course = crud.update_password_course(db=db, course_name=course_name, updated_password=update_password)
        
    except IntegrityError:
        
        raise HTTPException(status_code=400, detail="Integrity error")
    
    return {
        "status_code": 200,
        "detail": f"Password of the course {course_name} update."
    }
    
# Ruta para eliminar un curso '/professor/delete-course'
@professor_router.delete("/delete-course", response_model=dict)
def delete_course(course_name: str, professor: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not professor["role"] == "professor":
        
        raise HTTPException(
            status_code=403,
            detail="You're not a professor.",
        )
        
    course = crud.get_course_by_name(db=db, course_name=course_name)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    db_professor = crud.get_professor_by_username(db=db, username=professor["username"])
    
    if not course.professor_id == db_professor.professor_id:
        
        raise HTTPException(
            status_code=403,
            detail=f"The course '{course_name}' is not your course, you can't delete it.",
        )
        
    message = crud.delete_course(db=db, course_name=course_name)
    
    return {
        "status_code": 200,
        "message": message
    }
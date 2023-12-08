from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sql import schemes, crud
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from auth.token import get_current_user, get_db, validate_username

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

# Ruta para obtener todos los usuarios (students y professors)
@admin_router.get("/get-all-users", response_model=List[schemes.Professor | schemes.Student])
def get_all_users(payload: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
    
    try:
        return crud.get_all_users(db=db)
    except Exception as e:
        return str(e)
    
# Ruta para obtener todos los cursos '/admin/get-all-courses'
@admin_router.get("/get-all-courses", response_model=List[schemes.Course])
def get_all_courses(payload: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    try:
        courses = crud.get_all_courses(db=db)
    except Exception as e:
        return str(e)
    
    return courses

# Ruta para obtener los cursos de un estudiante '/admin/get-student-courses/{student_username}'
@admin_router.get("/get-student-courses/{student_username}", response_model=List[schemes.CourseResponse] | None)
def get_student_courses(student_username: str,
                        payload: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    student = crud.get_student_by_username(db=db, username=student_username)
    
    if not student:
        
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )
        
    try:
        student_courses = crud.get_course_info_of_student(db=db, student_username=student_username)
    except Exception as e:
        return str(e)
    
    return student_courses    

# Ruta para crear un profesor '/admin/create-professor'
@admin_router.post("/create-professor", response_model=schemes.ProfessorCreate)
def create_professor(professor: schemes.ProfessorCreate, payload: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    if validate_username(db=db, username=professor.username):
            
        raise HTTPException(
        status_code=409,
        detail="Username already exists.",
    )
        
    try:
        db_professor = crud.create_professor(db=db, professor=professor)
        
    except IntegrityError as e:
        
        error_message = str(e)
        
        if "Duplicate entry" in error_message:
            raise HTTPException(status_code=400, detail="Duplicate Entry")
        
        else:
            raise HTTPException(status_code=400, detail="Integrity error")
        
    return db_professor

# Ruta para crear un estudiante '/admin/create-student'.
@admin_router.post("/create-student", response_model=schemes.StudentCreate)
def create_student(student: schemes.StudentCreate, payload: dict = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    if validate_username(db=db, username=student.username):
            
        raise HTTPException(
        status_code=409,
        detail="Username already exists.",
    )
    
    try:
        db_student = crud.create_student(db=db, student=student)
    except IntegrityError as e:
        
        error_message = str(e)
        
        if "Duplicate entry" in error_message:
            raise HTTPException(status_code=400, detail="Duplicate Entry")
        
        else:
            raise HTTPException(status_code=400, detail="Integrity error")
        
    return db_student

# Ruta para crear un curso '/admin/create-course'
@admin_router.post("/create-course", response_model=schemes.CourseCreate)
def create_course(course: schemes.CourseCreate,
                  payload: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    db_course = crud.get_course_by_name(db=db, course_name=course.name)
    
    if db_course:
        
        raise HTTPException(
        status_code=409,
        detail="Name already exists.",
    )
        
    professor = crud.get_professor_by_id(db=db, professor_id=course.professor_id)
    
    if not professor:
        
        raise HTTPException(
        status_code=404,
        detail="Professor ID not found.",
    )
        
    try:
        course = crud.create_course(db=db, course=course)
    except IntegrityError as e:
        
        error_message = str(e)
        
        if "Duplicate entry" in error_message:
            raise HTTPException(status_code=400, detail="Duplicate Entry")
        
        else:
            raise HTTPException(status_code=400, detail="Integrity error")
        
    return course

# Ruta para inscribir un estudiante a un curso '/admin/inscribe-student'
@admin_router.post("/inscribe-student", response_model=schemes.InscriptionCreate)
def inscribe_student(inscription: schemes.InscriptionCreate,
                     payload: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
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
    
    if crud.verify_inscription_of_student(db=db, course_name=course.name, student_username=student.username):
        
        raise HTTPException(
            status_code=409,
            detail="The student is already enrolled in this course.",
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
    
# Ruta para editar la contraseña de un curso '/admin/update-password-course'
@admin_router.put("/update-password-course", response_model=dict)
def update_password_course(course_name: str,
                update_password: str,
                payload: dict = Depends(get_current_user),
                db: Session = Depends(get_db)):
    
    db_course = crud.get_course_by_name(db=db, course_name=course_name)
    
    if not payload["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
    
    if not db_course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    try:
        course = crud.update_password_course(db=db, course_name=course_name, updated_password=update_password)
        
    except IntegrityError:
        
        raise HTTPException(status_code=400, detail="Integrity error")
    
    return {
        "status_code": 200,
        "detail": f"Password of the course {course_name} update."
    }
    
# Ruta para eliminar un curso y sus inscripciones '/admin/delete-course'
@admin_router.delete("/delete-course", response_model=dict)
def delete_course(course_name: str, current_user: dict = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    
    if not current_user["role"] == "admin":
        
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource.",
        )
        
    course = crud.get_course_by_name(db=db, course_name=course_name)
    
    if not course:
        
        raise HTTPException(
            status_code=404,
            detail="Course not found.",
        )
        
    message = crud.delete_course(db=db, course_name=course_name)
    
    return {
        "status_code": 200,
        "message": message
    }
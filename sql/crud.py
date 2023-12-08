from sqlalchemy.orm import Session
from . import models, schemes
from auth.hash import hash_password

def get_admin_by_username(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

def get_student_by_username(db: Session, username: str):
    return db.query(models.Student).filter(models.Student.username == username).first()

def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()

def get_professor_by_username(db: Session, username: str):
    return db.query(models.Professor).filter(models.Professor.username == username).first()

def get_all_users(db: Session):
    
    students = db.query(models.Student).all()
    professors = db.query(models.Professor).all()
    
    return students + professors

def create_student(db: Session, student: schemes.StudentCreate):
    
    db_student = models.Student(
        username=student.username,
        name=student.name,
        full_name=student.full_name,
        phone_number=student.phone_number,
        password=hash_password(student.password),
        semester=student.semester,
        profile_picture=student.profile_picture,
        role=student.role
    )
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    return db_student

def get_professor_by_id(db: Session, professor_id: int):
    
    return db.query(models.Professor).filter(models.Professor.professor_id == professor_id).first()

def create_professor(db: Session, professor: schemes.ProfessorCreate):
    
    db_professor = models.Professor(
        username=professor.username,
        name=professor.name,
        full_name=professor.full_name,
        phone_number=professor.phone_number,
        password=hash_password(professor.password),
        profile_picture=professor.profile_picture,
        role=professor.role
    )
    
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    
    return db_professor

def create_course(db: Session, course: schemes.CourseCreate):
    
    db_course = models.Course(
        professor_id = course.professor_id,
        name = course.name,
        password = hash_password(course.password),
        description = course.description,
        semester = course.semester,
        program = course.program,
        profile_picture = course.profile_picture
    )
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    return db_course

def get_course_by_name(db: Session, course_name: str):
    
    return db.query(models.Course).filter(models.Course.name == course_name).first()

def get_course_by_id(db: Session, course_id: int):
    
    return db.query(models.Course).filter(models.Course.course_id == course_id).first()

def get_courses_of_professor(db: Session, professor_username: str):
    
    professor = get_professor_by_username(db=db, username=professor_username)
    
    return db.query(models.Course).filter(models.Course.professor_id == professor.professor_id)

def verify_inscription_of_student(db: Session, course_name: str, student_username: str):
    
    db_course = get_course_by_name(db=db, course_name=course_name)
    db_student = get_student_by_username(db=db, username=student_username)
    
    inscription = db.query(models.Inscription).filter(
    models.Inscription.course_id == db_course.course_id,
    models.Inscription.student == db_student
    ).first()
    
    if inscription:
        return True
    
    return False

def create_inscription(db: Session, inscription: schemes.InscriptionCreate):
    
    db_inscription = models.Inscription(
        student_id=inscription.student_id,
        course_id=inscription.course_id
    )
    
    db.add(db_inscription)
    db.commit()
    db.refresh(db_inscription)
    
    return db_inscription

def get_all_courses(db: Session):
    
    return db.query(models.Course).all()

def get_course_info_of_student(db: Session, student_username: str):
    student = get_student_by_username(db=db, username=student_username)
    
    course_info = db.query(
        models.Course.course_id,
        models.Course.name,
        models.Course.description,
        models.Course.semester,
        models.Course.program.label("program_name"),
        models.Professor.name.label("professor_name")
    ).join(models.Inscription).join(models.Professor).filter(
        models.Inscription.student_id == student.student_id
    ).all()
    
    courses = [{
        "course_id": info[0],
        "course_name": info[1],
        "description": info[2],
        "semester": info[3],
        "program_name": info[4],
        "professor_name": info[5]
    } for info in course_info]

    return courses

def get_students_of_course_by_name(db: Session, course_name: str):
    
    course = get_course_by_name(db=db, course_name=course_name)
    
    student_info = db.query(
        models.Student.student_id,
        models.Student.name,
        models.Student.full_name,
        models.Student.phone_number,
        models.Student.semester   
    ).join(models.Inscription).filter(
        models.Inscription.course_id  == course.course_id
    ).all()
    
    students = [{
        "student_id": info[0],
        "name": info[1],
        "full_name": info[2],
        "phone_number": info[3],
        "semester": info[4]
    } for info in student_info]

    return students

def update_password_course(db: Session, course_name: str, updated_password: str):
    
    db_course = get_course_by_name(db=db, course_name=course_name)

    if not db_course:
        return None 

    db_course.password = hash_password(updated_password)

    db.commit()
    db.refresh(db_course)

    return db_course

def delete_course(db: Session, course_name: str):
    
    course = get_course_by_name(db=db, course_name=course_name)
    
    inscriptions = db.query(models.Inscription).filter(models.Inscription.course_id == course.course_id).delete()
    
    db.delete(course)
    db.commit()
    
    return f"Course '{course_name}' deleted."
    
    
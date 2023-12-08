from pydantic import BaseModel
from typing import List
from datetime import datetime

class AdminBase(BaseModel):

    username: str
    name: str
    full_name: str
    phone_number: str
    profile_picture: str
    role: str = "admin"
    

class AdminCreate(AdminBase):
    
    password: str


class Admin(AdminBase):
    
    admin_id: int
    
    
    class Config:
        orm_mode = True

# Clase base
class StudentBase(BaseModel):
    
    username: str
    name: str
    full_name: str
    phone_number: str
    profile_picture: str
    semester: int
    role: str = "student"

# Clase para crear un estudiante
class StudentCreate(StudentBase):
    
    password: str
    
# Clase para obtener un estudiante
class Student(StudentBase):

    student_id: int
    
    class Config:
        orm_mode = True

class ProfessorBase(BaseModel):

    username: str
    name: str
    full_name: str
    phone_number: str
    profile_picture: str
    role: str = "professor" 

class ProfessorCreate(ProfessorBase):
    
    password: str


class Professor(ProfessorBase):
    
    class Config:
        orm_mode = True


class CourseBase(BaseModel):
    
    name: str
    description: str
    semester: int
    program: str
    professor_id: int

class CourseCreate(CourseBase):
    
    profile_picture: str
    password: str

class Course(CourseBase):

    course_id: int
    
    class Config:

        orm_mode = True

class InscriptionBase(BaseModel):
    
    student_id: int
    course_id: int

class InscriptionCreate(InscriptionBase):

    pass

class Inscription(InscriptionBase):

    inscription_id: int
    student: Student
    course: Course

    class Config:

        orm_mode = True


class TaskBase(BaseModel):
    
    course_id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    unique_filename: str
    active: bool

class TaskCreate(TaskBase):
    pass
    
class Task(TaskBase):

    task_id: int
    
    class Config:

        orm_mode = True


class NoteBase(BaseModel):

    note: float
    student_id: int
    task_id: int

class NoteCreate(NoteBase):

    pass


class Note(NoteBase):

    note_id: int

    class Config:
            
        orm_mode = True
        
class CourseResponse(BaseModel):
    course_id: int
    course_name: str
    description: str
    semester: int
    program_name: str
    professor_name: str
    
class StudentResponse(BaseModel):
    student_id: int
    name: str
    full_name: str
    phone_number: str
    semester: int
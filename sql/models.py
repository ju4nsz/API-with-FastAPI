from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base

class Admin(Base):
    
    __tablename__ = "admins"
    
    admin_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), index=True, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    full_name = Column(String(50), nullable=False)
    phone_number = Column(String(30), nullable=False)
    password = Column(String(70), nullable=False)
    profile_picture = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)

class Professor(Base):
    
    __tablename__ = "professors"
    
    professor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), index=True, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    full_name = Column(String(50), nullable=False)
    phone_number = Column(String(50), nullable=False)
    password = Column(String(70), nullable=False)
    profile_picture = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    
    # Relación con Course
    courses = relationship("Course", back_populates="professor")
    
class Student(Base):

    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(30), unique=True, nullable=False)
    password = Column(String(70), unique=True, nullable=False)
    semester = Column(Integer, unique=True, nullable=False)
    profile_picture = Column(String(255), unique=True, nullable=False)
    role = Column(String(30), nullable=False)
    
    # Relación con Inscription
    inscriptions = relationship("Inscription", back_populates="student")
    
    # Relación con notes
    notes = relationship("Note", back_populates="student")
    
class Inscription(Base):
    __tablename__ = "inscriptions"
    
    inscription_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    
    # Relación con Student
    student = relationship("Student", back_populates="inscriptions")
    
    # Relación con Course
    course = relationship("Course", back_populates="inscriptions")    
    
class Course(Base):

    __tablename__ = "courses"   

    course_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    professor_id = Column(Integer, ForeignKey("professors.professor_id"))
    name = Column(String(50), unique=True , nullable=False)
    password = Column(String(70), unique=True, nullable=False)
    description = Column(String(200), nullable=False)
    semester = Column(Integer, nullable=False)
    program = Column(String(50), nullable=False)
    profile_picture = Column(String(255), nullable=False)
    
    # Relación con Mister
    professor = relationship("Professor", back_populates="courses")
    
    # Relación con Inscription
    inscriptions = relationship("Inscription", back_populates="course")
    
    # Relación con Task
    tasks = relationship("Task", back_populates="course")

class Task(Base):

    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable = False)
    start_date = Column(DateTime, nullable = False)
    end_date = Column(DateTime, nullable = False)
    unique_filename = Column(String(50), nullable = False)
    active = Column(Boolean, nullable = False)
    
    # Relación con course
    course = relationship("Course", back_populates="tasks")
    
    # Relación con Note
    notes = relationship("Note", back_populates="task")

class Note(Base):

    __tablename__ = "notes"
    
    note_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    note = Column(DECIMAL(3,2), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    
    # Relación con student
    student = relationship("Student", back_populates="notes")
    
    # Relación con Task
    task = relationship("Task", back_populates="notes")
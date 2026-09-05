from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


class Student(BaseModel):
    name: str
    email: str
    skills: list[str]
    education: str
    experience: str


students = []


@router.post("/")
def add_student(student: Student):
    student_data = {
        "id": len(students) + 1,
        **student.model_dump()
    }

    students.append(student_data)

    return {
        "message": "Student added successfully",
        "student": student_data
    }


@router.get("/")
def get_students():
    return {
        "students": students
    }


@router.get("/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    return {
        "message": "Student not found"
    }
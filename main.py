from fastapi import FastAPI, Request, HTTPException, Body, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import uvicorn
from bson import ObjectId
from contextlib import asynccontextmanager

from database import students_collection, check_connection
from models import StudentCreate, StudentUpdate, Student

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await check_connection()
    yield
    # Shutdown: Clean up if needed
    pass

app = FastAPI(title="Student Manager Pro", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API Routes ---

@app.get("/api/students", response_description="List all students")
async def get_students():
    students = await students_collection.find().to_list(1000)
    # Convert _id to string for JSON serialization
    for student in students:
        student["_id"] = str(student["_id"])
    return students

@app.post("/api/students", response_description="Add new student")
async def create_student(student: StudentCreate = Body(...)):
    student_dict = student.model_dump()
    new_student = await students_collection.insert_one(student_dict)
    created_student = await students_collection.find_one({"_id": new_student.inserted_id})
    created_student["_id"] = str(created_student["_id"])
    return created_student

@app.put("/api/students/{student_id}", response_description="Update a student")
async def update_student(student_id: str, student: StudentUpdate = Body(...)):
    student_dict = {k: v for k, v in student.model_dump().items() if v is not None}

    if len(student_dict) >= 1:
        update_result = await students_collection.update_one(
            {"_id": ObjectId(student_id)}, {"$set": student_dict}
        )

        if update_result.modified_count == 1:
            updated_student = await students_collection.find_one({"_id": ObjectId(student_id)})
            if updated_student:
                updated_student["_id"] = str(updated_student["_id"])
                return updated_student

    existing_student = await students_collection.find_one({"_id": ObjectId(student_id)})
    if existing_student:
        existing_student["_id"] = str(existing_student["_id"])
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

@app.delete("/api/students/{student_id}", response_description="Delete a student")
async def delete_student(student_id: str):
    delete_result = await students_collection.delete_one({"_id": ObjectId(student_id)})

    if delete_result.deleted_count == 1:
        return {"message": "Student deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

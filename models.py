from pydantic import BaseModel, ConfigDict, Field, BeforeValidator, PlainSerializer
from typing import Optional, Annotated
from bson import ObjectId

# Simple validator to ensure ObjectId is converted to string and validated
def validate_object_id(v: any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)

# Pydantic-friendly ObjectId type
PyObjectId = Annotated[
    str, 
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str)
]

class StudentBase(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    age: int = Field(...)
    course: str = Field(...)
    grade: str = Field(...)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    course: Optional[str] = None
    grade: Optional[str] = None

class Student(StudentBase):
    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

from pydantic import BaseModel

class Task(BaseModel):
    title: str
    completed: bool = False
    created_by: str
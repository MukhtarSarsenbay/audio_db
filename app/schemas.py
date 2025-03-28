from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    id: int
    username: str
    email: Optional[str] = None

    class Config:
        from_attributes = True  
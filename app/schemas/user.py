from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
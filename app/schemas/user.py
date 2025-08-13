from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool

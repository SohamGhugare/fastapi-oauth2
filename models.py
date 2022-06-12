from sqlmodel import SQLModel, Field
from typing import Optional

class UserModel(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True) # Primary key
    username: str
    fullname: str
    email: Optional[str] = Field(default=None)
    hashed_password: str
    created_at: str
    disabled: bool = Field(default=False)

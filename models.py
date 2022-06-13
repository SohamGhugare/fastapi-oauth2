from sqlmodel import SQLModel, Field
from typing import Optional

class UserModel(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True) # Primary key
    username: str
    hashed_password: str
    disabled: bool = Field(default=False)

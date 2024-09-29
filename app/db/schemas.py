from pydantic import BaseModel

class UserBase(BaseModel):
    avatar_key: str
    username: str
    displayname: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
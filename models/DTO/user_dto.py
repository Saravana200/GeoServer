from pydantic import BaseModel

class UserLoginDto(BaseModel):
    name: str
    password: str
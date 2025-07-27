import jwt
import os
from fastapi import Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from service.repository import user_service_factory,UserService
from models import UserLoginDto,User
from .bcrypt import Hashing


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(token:str = Depends(oauth2_scheme),service:UserService = Depends(user_service_factory))->User:
    try:
        user_cred = jwt.decode(token,os.getenv("SECRET_KEY"),os.getenv("ALGORITHM"))
        return await service.get_user(user_cred["name"])
    except Exception as e:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid jwt token",
        )
         

async def register_user(user_dto:UserLoginDto = Body(...),service:UserService = Depends(user_service_factory))->str:
    user:User = await service.get_user(user_dto.name)
    if(user):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="user name already exists",
        )
    user_cred={
        "name": user_dto.name,
    }
    token = jwt.encode(user_cred,os.getenv("SECRET_KEY"),os.getenv("ALGORITHM"))
    user = User(name=user_dto.name,hashed_secret=Hashing.create_hash(user_dto.password),email=user_dto.name)
    await service.add_user(user)
    return token

async def login_user(user_dto:UserLoginDto = Body(...),service:UserService = Depends(user_service_factory))->str:
    user:User = await service.get_user(user_dto.name)
    if (user == None or not Hashing.validate_hase(user_dto.password,user.hashed_secret)):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="user name or password is invalid",
        )
    user_cred={
        "name": user_dto.name,
    }
    token = jwt.encode(user_cred,os.getenv("SECRET_KEY"),os.getenv("ALGORITHM"))
    return token
        





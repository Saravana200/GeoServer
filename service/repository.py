from .user_service import UserService
from .soil_moisture_service import SoilMoistureService
from .soil_aridity_service import SoilAridityService
from .postgres_connector import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def user_service_factory(session:AsyncSession=Depends(async_session)):
    return UserService(_session=session)

async def soil_moisture_service_factory(sesssion: AsyncSession = Depends(async_session)):
    return SoilMoistureService(_session=sesssion)

async def soil_aridity_service_factory(sesssion: AsyncSession = Depends(async_session)):
    return SoilAridityService(_session=sesssion)
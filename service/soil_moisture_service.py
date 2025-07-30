from sqlalchemy.ext.asyncio import AsyncSession
from models.DTO import Coordinates
from models import soil_moisture
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

class SoilMoistureService:
    def __init__(self, _session: AsyncSession):
        self.session = _session
    
    async def save_soil_moisture(self,user_id:int,value:float,coordinates:Coordinates)->bool:
        try:
            entry = soil_moisture.SoilMoisture(
                lat=coordinates.lat,
                long=coordinates.long,
                user_id=user_id,
                value=value
            )
            self.session.add(entry)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            print(f"Failed to save soil moisture: {e}")
            raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"failed to save to db;{e}")
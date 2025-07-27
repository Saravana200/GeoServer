from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .Base import Base
from datetime import datetime

class SoilAridity(Base):
    __tablename__ = "soil_aridity"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    lat: Mapped[float]
    long: Mapped[float]
    value: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="soil_aridity")

    def __repr__(self) -> str:
        return (
            f"User(id={self.user_id!r}, name={self.user.name!r}, " f"email={self.user.email!r})" 
            f"\n SoilAridity(aridity_value={self.value},lat={self.lat},long={self.long})"
        )

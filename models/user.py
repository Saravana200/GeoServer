from sqlalchemy.orm import Mapped, mapped_column,relationship
from .Base import Base

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    hashed_secret: Mapped[str]

    soil_moisture: Mapped[list["SoilMoisture"]] = relationship(back_populates="user")
    soil_aridity: Mapped[list["SoilAridity"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r})"
        )

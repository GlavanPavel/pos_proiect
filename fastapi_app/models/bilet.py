from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_app.services.database import Base

# sqlalchemy 2.0
class Bilet(Base):
    __tablename__ = "bilet"

    cod: Mapped[str] = mapped_column(String(25), primary_key=True, index=True)
    # Optional[] - pot fi nule
    pachetID: Mapped[Optional[int]] = mapped_column(ForeignKey("pachet.id"))
    evenimentID: Mapped[Optional[int]] = mapped_column(ForeignKey("eveniment.id"))

    eveniment: Mapped[Optional["Eveniment"]] = relationship(back_populates="bilete")
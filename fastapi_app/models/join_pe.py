from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_app.core.database import Base

class JoinPE(Base):
    __tablename__ = "join_pe"

    pachetID: Mapped[int] = mapped_column(ForeignKey("pachet.id"), primary_key=True)
    evenimentID: Mapped[int] = mapped_column(ForeignKey("eveniment.id"), primary_key=True)
    numarLocuri: Mapped[int]

    pachet: Mapped["Pachet"] = relationship(
        back_populates="pachet_associations"
    )

    eveniment: Mapped["Eveniment"] = relationship(
        back_populates="eveniment_associations"
    )
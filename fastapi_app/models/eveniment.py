from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from fastapi_app.services.database import Base

class Eveniment(Base):
    __tablename__ = "eveniment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    id_owner: Mapped[int]
    nume: Mapped[str] = mapped_column(String(255))
    locatie: Mapped[str] = mapped_column(String(255))
    descriere: Mapped[str] = mapped_column(String(255))
    numarLocuri: Mapped[int]

    bilete: Mapped[List["Bilet"]] = relationship(back_populates="eveniment")

    eveniment_associations: Mapped[List["JoinPE"]] = relationship(
        back_populates="eveniment"
    )

    pachete: Mapped[List["Pachet"]] = association_proxy(
        "eveniment_associations", "pachet"
    )
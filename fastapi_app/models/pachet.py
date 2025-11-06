from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from fastapi_app.core.database import Base

class Pachet(Base):
    __tablename__ = "pachet"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    id_owner: Mapped[int]
    nume: Mapped[str] = mapped_column(String(255))
    locatie: Mapped[str] = mapped_column(String(255))
    descriere: Mapped[str] = mapped_column(String(255))

    pachet_associations: Mapped[List["JoinPE"]] = relationship(
        back_populates="pachet"
    )

    evenimente: Mapped[List["Eveniment"]] = association_proxy(
        "pachet_associations", "eveniment"
    )
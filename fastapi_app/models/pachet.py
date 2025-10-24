from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_app.services.database import Base

class Pachet(Base):
    __tablename__ = "pachet"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    id_owner: Mapped[int]
    nume: Mapped[str] = mapped_column(String(255))
    locatie: Mapped[str] = mapped_column(String(255))
    descriere: Mapped[str] = mapped_column(String(255))

    #TODO: Relationship between pachet and eveniment through join_pe
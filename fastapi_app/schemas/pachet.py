from pydantic import BaseModel, ConfigDict

class Pachet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_owner: int
    nume: str
    locatie: str
    descriere: str
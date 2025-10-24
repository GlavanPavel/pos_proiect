from pydantic import BaseModel, ConfigDict

class Bilet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cod: str
    pachetID: int
    evenimentID: int
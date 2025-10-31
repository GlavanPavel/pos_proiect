from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from fastapi_app.schemas.link import Link


class BiletSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cod: str
    pachetID: Optional[int] = None
    evenimentID: Optional[int] = None

class BiletCreate(BaseModel):
    pachetID: Optional[int] = None
    evenimentID: Optional[int] = None

class BiletLinks(BaseModel):
    self: Link
    parent: Link

class BiletWithLinks(BiletSchema):
    links: BiletLinks = Field(..., alias="_links")

class BiletResponse(BaseModel):
    ticket: BiletWithLinks
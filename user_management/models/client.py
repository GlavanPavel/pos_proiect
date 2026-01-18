from typing import Annotated, Optional, List
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class ClientNameModel(BaseModel):
    nume: str = Field(...)
    prenume: str = Field(...)
    is_public: bool = Field(default=False)

class LinkSocialModel(BaseModel):
    url: str = Field(...)
    is_public: bool = Field(default=False)

class BiletModel(BaseModel):
    cod_bilet: str = Field(...)
    nume_eveniment: Optional[str] = None
    locatie: Optional[str] = None

class ClientModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr = Field(...)
    nume_client: Optional[ClientNameModel] = None
    links_social: List[LinkSocialModel] = Field(default_factory=list) # optional
    lista_bilete: List[BiletModel] = Field(...) # obligatoriu
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "nume_client": {
                    "prenume": "Jane",
                    "nume": "Doe",
                    "is_public": True
                },
                "links_social": [
                    {"url": "https://ferestre.com", "is_public": True},
                    {"url": "https://ok.com", "is_public": False}
                ],
                "lista_bilete": [
                    {"cod_bilet": "ab1234", "nume_eveniment": "Concert Rock", "locatie": "Bucuresti"},
                    {"cod_bilet": "ba4321"}
                ]
            }
        }
    )


class UpdateClientModel(BaseModel):
    email: Optional[EmailStr] = None
    nume_client: Optional[ClientNameModel] = None
    links_social: Optional[List[LinkSocialModel]] = None
    lista_bilete: Optional[List[BiletModel]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class ClientCollection(BaseModel):
    clienti: List[ClientModel]

class ClientResponseModel(ClientModel):
    links: Optional[dict] = Field(default=None, alias="_links")
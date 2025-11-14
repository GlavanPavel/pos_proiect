from fastapi import APIRouter, status, Body, HTTPException
from fastapi.responses import JSONResponse
import httpx
from bson import ObjectId
from user_management.core import config

from user_management.models import ClientModel, ClientCollection
from user_management.core import client_collection

router = APIRouter()

@router.post(
    "/clienti/",
    response_description="Adauga un nou client",
    response_model=ClientModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_client(client: ClientModel = Body(...)):
    new_client = client.model_dump(by_alias=True, exclude=["id"], exclude_none=True)
    result = await client_collection.insert_one(new_client)
    new_client["_id"] = result.inserted_id

    return new_client

@router.get(
    "/clienti/",
    response_description="Afiseaza toti clientii",
    response_model=ClientCollection,
    response_model_by_alias=False,
)
async def list_clienti():
    return ClientCollection(clienti=await client_collection.find().to_list(1000))

@router.delete(
    "/clienti/",
    response_description="Sterge toti clienti",
)
async def delete_clienti():
    delete_result = await client_collection.delete_many({})
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"numar_clienti_stersi": delete_result.deleted_count}
    )


@router.post(
    "/clienti/{client_id}/bilete/{cod_bilet}/validate",
    response_description="Validarea unui bilet achizitionat de un client",
    status_code=status.HTTP_200_OK
)
async def validate_ticket(client_id: str, cod_bilet: str):
    try:
        client_doc = await client_collection.find_one(
            {"_id": ObjectId(client_id), "lista_bilete.cod_bilet": cod_bilet}
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID-ul clientului este invalid")

    if not client_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clientul cu ID {client_id} si biletul {cod_bilet} nu a fost gasit."
        )

    bilet_url = f"{config.EVENIMENTE_SERVICE_URL}/event-manager/tickets/{cod_bilet}"

    try:
        async with httpx.AsyncClient() as s2s_client:
            response = await s2s_client.get(bilet_url)

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Eroare de la serviciul de evenimente: {e.response.json()}"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviciul de evenimente nu este disponibil."
        )
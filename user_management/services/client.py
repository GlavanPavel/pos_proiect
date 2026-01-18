import grpc
import httpx
from bson import ObjectId
from fastapi import HTTPException, status, Request, Response

from auth_service.generated import auth_pb2_grpc, auth_pb2
from user_management.core import client_collection, config
from user_management.core.security import get_system_token
from user_management.enums.UserRole import UserRole
from user_management.models import ClientModel
from user_management.models.client import UpdateClientModel
from user_management.schemas.bilet import BiletCreate


def create_links(client_id: str, request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "self": {"href": f"{base_url}/clienti/{client_id}", "method": "GET"},
        "update": {"href": f"{base_url}/clienti/{client_id}", "method": "PUT"},
        "delete": {"href": f"{base_url}/clienti/{client_id}", "method": "DELETE"},
        "tickets": {"href": f"{base_url}/clienti/{client_id}/bilete", "method": "GET"}
    }


async def get_all_clients(limit: int = 1000):
    return await client_collection.find().to_list(limit)


async def create_new_client(client: ClientModel, request: Request):
    client_data = client.model_dump(by_alias=True, exclude=["id"], exclude_none=True)
    result = await client_collection.insert_one(client_data)
    client_data["_id"] = result.inserted_id
    client_data["_links"] = create_links(str(result.inserted_id), request)
    return client_data


async def delete_all_clients():
    result = await client_collection.delete_many({})
    return result.deleted_count


async def get_client_with_links(id: str, request: Request, user_email: str, role: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalid")

    client = await client_collection.find_one({"_id": ObjectId(id)})
    if not client:
        raise HTTPException(status_code=404, detail=f"Clientul {id} nu a fost gasit")

    if role == UserRole.ADMIN:
        pass
    elif role == UserRole.CLIENT:
        if client["email"] != user_email:
            raise HTTPException(status_code=403, detail="Acces interzis: Nu puteti vizualiza profilul altui client")
    elif role == UserRole.OWNER:
        client = _filter_public_data(client)

    client["_links"] = create_links(id, request)
    return client


async def update_client_with_links(id: str, client_update: UpdateClientModel, request: Request, user_email: str, role: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalid")

    existing_client = await client_collection.find_one({"_id": ObjectId(id)})
    if not existing_client:
        raise HTTPException(status_code=404, detail="Clientul nu a fost gasit")

    if role != UserRole.ADMIN and existing_client["email"] != user_email:
        raise HTTPException(status_code=403, detail="Nu aveti permisiunea de a modifica acest profil")

    update_data = client_update.model_dump(exclude_none=True)
    if len(update_data) >= 1:
        update_result = await client_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data},
            return_document=True
        )
        update_result["_links"] = create_links(id, request)
        return update_result

    existing_client["_links"] = create_links(id, request)
    return existing_client


async def delete_single_client(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalid")

    delete_result = await client_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Clientul {id} nu a fost gasit")


async def get_client_tickets(id: str, user_email: str, role: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalid")

    client = await client_collection.find_one({"_id": ObjectId(id)})
    if not client:
        raise HTTPException(status_code=404, detail="Clientul nu a fost gasit")

    if role != UserRole.ADMIN and client["email"] != user_email:
        raise HTTPException(status_code=403, detail="Acces interzis la lista de bilete")

    return {"lista_bilete": client.get("lista_bilete", [])}


async def validate_ticket_external(client_id: str, cod_bilet: str, user_email: str, role: str, token: str):
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID client invalid")

    query = {"_id": ObjectId(client_id), "lista_bilete.cod_bilet": cod_bilet}
    if role == UserRole.CLIENT:
        query["email"] = user_email

    client_doc = await client_collection.find_one(query)

    if not client_doc:
        raise HTTPException(status_code=404, detail="Biletul nu a fost gasit in contul acestui client")

    ticket_url = f"{config.EVENIMENTE_SERVICE_URL}/tickets/{cod_bilet}"

    try:
        async with httpx.AsyncClient() as s2s_client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await s2s_client.get(ticket_url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Validare esuata in serviciul SQL")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Serviciul de Evenimente este indisponibil")


async def buy_ticket_for_client(client_id: str, ticket_data: BiletCreate, user_email: str, role: str):
    client = await client_collection.find_one({"_id": ObjectId(client_id)})
    if role == UserRole.CLIENT and client["email"] != user_email:
        raise HTTPException(status_code=403, detail=f"user_email:{user_email}, client_email:{client['email']}")

    system_token = await get_system_token()

    async with httpx.AsyncClient() as s2s_client:
        headers = {"Authorization": f"Bearer {system_token}"}
        response = await s2s_client.post(
            f"{config.EVENIMENTE_SERVICE_URL}/event-manager/tickets/",
            json=ticket_data.model_dump(),
            headers=headers
        )

        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Eroare la rezervarea locului")

        ticket_info = response.json()
        ticket_cod = ticket_info["ticket"]["cod"]

    await client_collection.update_one(
        {"_id": ObjectId(client_id)},
        {"$push": {"lista_bilete": {"cod_bilet": ticket_cod}}}
    )

    return ticket_info


def _filter_public_data(client_doc: dict):
    # filtrare nume
    nume_client = client_doc.get("nume_client", {})
    if not nume_client.get("is_public", False):
        client_doc["nume_client"] = None

    # filtrare link-uri sociale
    links = client_doc.get("links_social", [])
    client_doc["links_social"] = [l for l in links if l.get("is_public", False)]

    client_doc["email"] = "Hidden"

    return client_doc


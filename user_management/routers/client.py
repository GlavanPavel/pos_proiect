from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from user_management.core.security import role_required, verify_authorization
from user_management.enums.UserRole import UserRole
from user_management.models import ClientModel, ClientCollection
from user_management.models.client import ClientResponseModel, UpdateClientModel
from user_management.schemas.bilet import BiletCreate
from user_management.services.client import get_all_clients, create_new_client, delete_all_clients, \
    get_client_with_links, update_client_with_links, delete_single_client, get_client_tickets, validate_ticket_external, \
    buy_ticket_for_client

router = APIRouter(prefix="/clienti", tags=["clienti"])
security = HTTPBearer()

@router.get(
    "/",
    name="get_all_clients",
    response_model=ClientCollection,
    response_model_by_alias=False,
    # clientul nu ar trebui sa aiba acces, dar va avea
    dependencies=[Depends(role_required([UserRole.ADMIN, UserRole.CLIENT]))]
)
async def get_all_clients_route():
    clients_list = await get_all_clients()
    return ClientCollection(clienti=clients_list)

@router.post(
    "/",
    name="create_client",
    response_model=ClientResponseModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
    dependencies=[Depends(role_required([UserRole.ADMIN]))]
)
async def create_client_route(
    request: Request,
    client: ClientModel = Body(...)
):
    return await create_new_client(client, request)

@router.delete(
    "/",
    name="delete_all_clients",
    dependencies=[Depends(role_required([UserRole.ADMIN]))]
)
async def delete_all_clients_route():
    deleted_count = await delete_all_clients()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"numar_clienti_stersi": deleted_count}
    )

@router.get(
    "/{id}",
    name="get_client",
    response_model=ClientResponseModel,
    response_model_by_alias=False,
)
async def get_client_route(
    id: str,
    request: Request,
    user: dict = Depends(verify_authorization)
):
    return await get_client_with_links(
        id,
        request,
        user_email=user["user_email"],
        role=user["role"]
    )

@router.put(
    "/{id}",
    name="update_client",
    response_model=ClientResponseModel,
    response_model_by_alias=False,
)
async def update_client_route(
    id: str,
    request: Request,
    client_update: UpdateClientModel = Body(...),
    user: dict = Depends(role_required([UserRole.ADMIN, UserRole.CLIENT]))
):
    return await update_client_with_links(
        id,
        client_update,
        request,
        user_email=user["user_email"],
        role=user["role"]
    )
@router.delete(
    "/{id}",
    name="delete_client",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required([UserRole.ADMIN]))]
)
async def delete_client_route(id: str):
    return await delete_single_client(id)

@router.get(
    "/{id}/bilete",
    name="get_client_tickets",
)
async def get_client_tickets_route(
        id: str,
        user: dict = Depends(verify_authorization)
    ):
    return await get_client_tickets(id, user_email=user["user_email"], role=user["role"])
@router.post(
    "/{client_id}/bilete/{cod_bilet}/validate",
    name="validate_client_ticket",
    status_code=status.HTTP_200_OK
)
async def validate_client_ticket_route(
    client_id: str,
    cod_bilet: str,
    creds: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(verify_authorization)
):
    return await validate_ticket_external(
        client_id,
        cod_bilet,
        user_email=user["user_email"],
        role=user["role"],
        token=creds.credentials
    )

@router.post(
    "/{id}/bilete",
    name="buy_ticket",
    status_code=status.HTTP_201_CREATED
)
async def buy_ticket_route(
    id: str,
    ticket_data: BiletCreate,
    user: dict = Depends(role_required([UserRole.CLIENT, UserRole.ADMIN]))
):
    return await buy_ticket_for_client(
        client_id=id,
        ticket_data=ticket_data,
        user_email=user["user_email"],
        role=user["role"]
    )
from fastapi import APIRouter, Request, Depends, status
from .deps import SessionDep
from fastapi_app import services
from fastapi_app.schemas.bilet import BiletResponse, BiletCreate
from fastapi_app.core.security import verify_authorization, role_required
from ..core.RoleChecker import RoleChecker
from ..enums.UserRole import UserRole

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get(
    "/{cod}",
    name="get_ticket",
    response_model=BiletResponse
)
async def get_ticket_route(
        cod: str,
        session: SessionDep,
        request: Request,
        user: dict = Depends(verify_authorization)
):
    return await services.get_ticket(cod, session, request, user_id=user["user_id"], role=user["role"])

@router.post(
    "/",
    name="create_ticket",
    response_model=BiletResponse,
    status_code=status.HTTP_201_CREATED,
dependencies=[Depends(role_required([UserRole.ADMIN, UserRole.SERVICE_CLIENTI]))]
)
async def create_ticket_route(
        data: BiletCreate,
        session: SessionDep,
        request: Request,
):
    return await services.create_ticket(data, session, request)

@router.put(
    "/{cod}",
    name="update_ticket",
    response_model=BiletResponse
)
async def update_ticket_route(
        cod: str,
        data: BiletCreate,
        session: SessionDep,
        request: Request,
        user: dict = Depends(RoleChecker(["admin", "owner-event"]))
):
    return await services.update_ticket(cod, data, session, request, user_id=user["user_id"], role=user["role"])

@router.delete(
    "/{cod}",
    name="delete_ticket",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ticket_route(
        cod: str,
        session: SessionDep,
        user: dict = Depends(RoleChecker(["admin", "owner-event"]))
):
    return await services.delete_ticket(cod, session, user_id=user["user_id"], role=user["role"])
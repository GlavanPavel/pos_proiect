from fastapi import HTTPException, Depends, status, Request
from .security import verify_authorization
from sqlalchemy import select
from ..models import Eveniment

class RoleChecker:
    def __init__(self, allowed_roles: list[str], check_ownership: bool = False):
        self.allowed_roles = allowed_roles
        self.check_ownership = check_ownership

    async def __call__(
        self,
        request: Request,
        user_data: dict = Depends(verify_authorization)
    ):
        if user_data["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acces interzis. Roluri permise: {self.allowed_roles}"
            )

        if self.check_ownership and user_data["role"] == "owner-event":
            event_id = request.path_params.get("id")
            if event_id:
                from .database import sessionmanager

                async with sessionmanager.session() as session:
                    is_owner = await self._verify_resource_ownership(
                        session,
                        int(event_id),
                        int(user_data["user_id"])
                    )

                if not is_owner:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Nu sunteti proprietarul acestui eveniment"
                    )

        return user_data

    async def _verify_resource_ownership(self, session, resource_id: int, user_id: int) -> bool:

        stmt = select(Eveniment.id_owner).where(Eveniment.id == resource_id)
        result = await session.execute(stmt)
        db_owner_id = result.scalar_one_or_none()

        if db_owner_id is None:
            return False

        return db_owner_id == user_id
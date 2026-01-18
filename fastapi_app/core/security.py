from typing import List

import grpc
import auth_service.generated.auth_pb2 as auth_pb2
import auth_service.generated.auth_pb2_grpc as auth_pb2_grpc

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi_app.enums.UserRole import UserRole

security = HTTPBearer()

_channel = None

async def get_grpc_stub():
    global _channel
    if _channel is None:
        _channel = grpc.aio.insecure_channel('idm-service:50051')
    return auth_pb2_grpc.AuthServiceStub(_channel)


async def verify_authorization(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials

    stub = await get_grpc_stub()
    try:
        response = await stub.ValidateToken(auth_pb2.TokenRequest(token=token))

        if response.message != "Token valid":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response.message
            )

        return {"user_id": response.user_id, "user_email": response.sub, "role": response.role}

    except grpc.aio.AioRpcError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviciul de autentificare gRPC este indisponibil"
        )


def role_required(allowed_roles: List[UserRole]):
    def decorator(user_data: dict = Security(verify_authorization)):
        if user_data["role"] not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acces interzis. Roluri necesare: {[r.value for r in allowed_roles]}"
            )
        return user_data
    return decorator


from typing import List

import grpc
import auth_service.generated.auth_pb2 as auth_pb2
import auth_service.generated.auth_pb2_grpc as auth_pb2_grpc

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from user_management.core import config
from user_management.enums.UserRole import UserRole

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

        return {"user_email": response.sub, "role": response.role}

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

async def get_system_token():
    stub = await get_grpc_stub()
    try:
        response = await stub.Login(auth_pb2.LoginRequest(
            username=config.SERVICE_USERNAME,
            password=config.SERVICE_PASSWORD
        ))
        return response.token_value
    except grpc.aio.AioRpcError as e:
        print(f"DEBUG: Eroare gRPC la Login Serviciu: {e.code()} - {e.details()}")
        raise HTTPException(status_code=503, detail="Eroare IDM: Nu s-a putut genera token-ul de sistem")



import grpc
import logging
from concurrent import futures

from sqlalchemy import select

from .auth import (
    verify_password,
    generate_token,
    verify_token,
    token_blacklist
)
import auth_service.generated.auth_pb2 as auth_pb2
import auth_service.generated.auth_pb2_grpc as auth_pb2_grpc
from auth_service.database import sessionmanager
from auth_service.models.idm_models import User


class AuthService(auth_pb2_grpc.AuthServiceServicer):

    async def Login(self, request, context):
        async with sessionmanager.session() as session:
            stmt = select(User).where(User.username == request.username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or not verify_password(request.password, user.password):
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Credentiale invalide")

            token = generate_token(email=user.username, role=user.role.value, user_id=user.uid)

            return auth_pb2.TokenResponse(token_value=token)

    async def ValidateToken(self, request, context):
        try:
            payload = verify_token(request.token)

            return auth_pb2.UserIdentity(
                sub=payload["sub"],
                role=payload["role"],
                user_id=payload["id"],
                message="Token valid"
            )
        except Exception as e:
            return auth_pb2.UserIdentity(
                sub="",
                role="",
                message=str(e)
            )

    async def Logout(self, request, context):
        token = request.token
        token_blacklist.add(token)

        return auth_pb2.LogoutResponse(
            success=True,
            message="Token invalidat cu succes"
        )


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)

    server.add_insecure_port('[::]:50051')
    logging.info("Serverul IDM gRPC a pornit pe portul 50051")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.info("Server oprit")
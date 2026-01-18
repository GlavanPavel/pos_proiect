import jwt
import uuid
import os
import grpc
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ISSUER = os.getenv("ISSUER")

token_blacklist = set()


def generate_token(user_id: int, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'iss': ISSUER,
        'sub': email,
        'id': user_id,
        'exp': now + timedelta(hours=1),
        'jti': str(uuid.uuid4()),
        'role': role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    if token in token_blacklist:
        raise Exception("Token-ul e in blacklist")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], issuer=ISSUER)
        return payload
    except jwt.ExpiredSignatureError:
        token_blacklist.add(token)
        raise Exception("Token expirat")
    except jwt.InvalidTokenError:
        raise Exception("Token invalid")


def auth_required(f):
    @wraps(f)
    async def decorated(self, request, context):
        metadata = dict(context.invocation_metadata())

        if 'authorization' not in metadata:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Authorization token is missing")

        token_str = metadata['authorization']
        if token_str.startswith("Bearer "):
            token_str = token_str[7:]

        try:
            payload = verify_token(token_str)
            context.user_email = payload['sub']
            context.user_role = payload['role']
        except grpc.RpcError as e:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))

        return await f(self, request, context)

    return decorated


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
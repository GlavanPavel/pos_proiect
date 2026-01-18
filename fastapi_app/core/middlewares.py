from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.middleware.cors import CORSMiddleware

request_object: ContextVar[Request] = ContextVar('request')

class PaginationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_object.set(request)
        response = await call_next(request)
        return response

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(PaginationMiddleware)
]
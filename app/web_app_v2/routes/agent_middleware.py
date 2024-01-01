from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = "a1621e69-970a-4340-86e7-778d82e2137b"
        Request.state.user_id = user_id
        response = await call_next(request)
        return response

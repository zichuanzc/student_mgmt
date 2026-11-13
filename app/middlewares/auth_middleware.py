from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse

from app.core.config import WHITE_PREFIXES





class AuthMiddleware(BaseHTTPMiddleware):
    """鉴权中间件"""
    def __init__(self, app, white_prefixes: tuple[str, ...] = WHITE_PREFIXES, ui_prefix: str = "/ui", token: str = "abcd"):
        super().__init__(app)
        self.white_prefixes = tuple(white_prefixes)
        self.ui_prefix = ui_prefix
        self.token = token

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path.rstrip("/") or "/"

        # 访问前端页面时种令牌，浏览器后续同源请求会自动携带
        if path.startswith(self.ui_prefix):
            response = await call_next(request)
            response.set_cookie(
                "token", self.token,
                httponly=True,
                samesite="lax",
                max_age=8 * 3600,
            )
            return response

        if path == "/" or path.startswith(self.white_prefixes):
            return await call_next(request)

        # 两种凭证都接受：Header（Swagger 里手填）或 Cookie（浏览器自动带）
        auth = request.headers.get("Authorization", "")
        scheme, _, header_token = auth.partition(" ")
        cookie_token = request.cookies.get("token")
        token = header_token if scheme.lower() == "bearer" and header_token else cookie_token
        if not token:
            return JSONResponse(status_code=401, content={"code": 401, "message": "认证令牌缺失或格式错误", "data": None})
        if token != self.token:
            return JSONResponse(status_code=401, content={"code": 401, "message": "令牌已失效", "data": None})

        return await call_next(request)
"""自定义 OpenAPI：让 Swagger 文档支持填 Bearer token"""
from fastapi.openapi.utils import get_openapi


def build_openapi(app):
    def custom_openapi():
        # 有缓存就直接返回，避免每次请求重新生成
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            summary=getattr(app, "summary", None),
            description=getattr(app, "description", None),
            routes=app.routes,
        )

        schema.setdefault("components", {})
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        # 全局挂 security：文档里所有接口默认关联这个 auth
        schema["security"] = [{"BearerAuth": []}]

        app.openapi_schema = schema
        return schema

    return custom_openapi

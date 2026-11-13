from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import WHITE_PREFIXES, VERSION
from app.core.custom_openapi import build_openapi
from app.core.database import Base, engine
from app.core.exception_handlers import register_exception_handlers
from app.middlewares.auth_middleware import AuthMiddleware

import app.models  # noqa: F401  仅为注册 ORM 映射

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
OPENAPI_URL = "/student.com"          # 自定义 schema 路径，记得进白名单
UI_PREFIX = "/ui"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 建表放这里：import 阶段不连库，reload 也不会在导入时炸
    Base.metadata.create_all(engine)
    yield

# 实例化一个FastAPI app对象
app = FastAPI(
    title="学生管理系统",
    version=VERSION,
    summary="学生管理系统",
    description="""这是一个基于 FastAPI 的学生管理系统，提供学生基本信息管理、考核成绩管理和就业管理三大核心功能模块。
    系统采用 RESTFUL API 设计，支持前后端分离架构。""",
    openapi_url=OPENAPI_URL,
    lifespan=lifespan,
)

# 添加鉴权中间件，先加（内层），处理token
app.add_middleware(AuthMiddleware, white_prefixes=WHITE_PREFIXES, ui_prefix=UI_PREFIX)

# 添加跨域中间件，后加（外层），预检请求由 CORS 先处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 同源访问够用；若前端独立端口，改成具体 origin
    allow_credentials=False,    # 与 "*" 互斥；用 Cookie 时必须改 True + 具体 origin
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)  # 添加全局异常处理
app.include_router(api_router)  # 注册路由

if FRONTEND_DIR.exists():
    app.mount(UI_PREFIX, StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    print(f"[WARN] 前端目录不存在，/ui 将不可用：{FRONTEND_DIR}")



# 必须在 include_router 之后赋值，保证 schema 包含全部路由
app.openapi = build_openapi(app)

# 测试阶段，同局域网其他设备访问：reload=False
# 自己开发时需要注释掉，用命令行启动：uvicorn app.main:app --reload
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

# 真是的
# 再来一次
# 摇光又来了
from fastapi import APIRouter

from .user import router as user_router
from .student import router as student_router
from .score import s_router
from .employment import router as employment_router
from .class_ import router as class_router
from .teacher import router as teacher_router
from .statistic import statistic_router

from app.core.config import MAIN_VERSION



v1_router = APIRouter(prefix=f"/{MAIN_VERSION}")
v1_router.include_router(user_router)
v1_router.include_router(student_router)
v1_router.include_router(s_router)
v1_router.include_router(employment_router)
v1_router.include_router(class_router)
v1_router.include_router(teacher_router)
v1_router.include_router(statistic_router)


from fastapi import APIRouter

from .subject import router as subject_router
from .course import router as course_router
from .score import router as score_router


s_router = APIRouter(prefix="/score", tags=["成绩管理模块"])
s_router.include_router(subject_router)
s_router.include_router(course_router)
s_router.include_router(score_router)
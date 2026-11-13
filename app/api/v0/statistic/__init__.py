from fastapi import APIRouter
from .basic_info import router as basic_info_router
from .score import router as score_router
from .employment import router as employment_router

statistic_router = APIRouter(prefix="/statistic", tags=["统计分析模块"])
statistic_router.include_router(basic_info_router)
statistic_router.include_router(score_router)
statistic_router.include_router(employment_router)
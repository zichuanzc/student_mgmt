from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dao.basic_info import get_student_older, get_class_gender_stat
from typing import Optional
from app.schemas.base import ApiResponse,PageResponse
from app.schemas.statistic.basic_info import  ClassGenderStatResponse,StudentOlderResponse


router = APIRouter(prefix="/basic_info", tags=["基础信息统计"])

@router.get("/student_older",response_model=ApiResponse[PageResponse[StudentOlderResponse]],summary="查询指定年龄以上学员，默认返回全部")
async def student_older(
        db: Session = Depends(get_db),
        age_threshold: Optional[int] = None,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    if age_threshold is not None:
        if age_threshold < 0 or age_threshold > 120:
            raise HTTPException(status_code=400, detail="年龄阈值非法，取值范围0~120")
    rows,total= get_student_older(db,page,page_size,age_threshold)
    return {"code": 200,
        "message":"查询成功",
        "data": {
        'total': total,
        'page': page,
        'size': page_size,
        'data': rows
              }
    }

@router.get("/class_gender", response_model=ApiResponse[PageResponse[ClassGenderStatResponse]],summary="各班人数、男女统计")
async def class_gender(db: Session = Depends(get_db),
                       page: int = Query(1, ge=1, description="页码"),
                       page_size: int = Query(10, ge=1, le=100, description="每页数量")
                       ):
    rows, total = get_class_gender_stat(db,page, page_size)
    return ApiResponse(
        code=200,
        message = "查询成功",
        data = {
        'total': total,
        'page': page,
        'size': page_size,
        'data': rows
              }
    )





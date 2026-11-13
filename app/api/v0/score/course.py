# 负责路由：课程 course

from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from app.dao import course as course_dao
from app.schemas.base import ApiResponse
from app.schemas.course import (
    CourseCreateRequest,
    CourseListResponse,
    CourseOut,
    CourseUpdateRequest,
)

router = APIRouter(prefix="/course", tags=["课程管理"])



@router.post("", response_model=ApiResponse[CourseOut], summary="新增课程", status_code=201)
def create_course(data: CourseCreateRequest, db=Depends(get_db)):
    try:
        course = course_dao.create_course(db, data)
    except ValueError as e:  # 班级/科目/老师不存在、时间倒挂、重复排课
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 201, "message": "创建成功", "data": course}


@router.put("/{course_id}", response_model=ApiResponse[CourseOut], summary="修改课程")
def update_course(course_id: int, data: CourseUpdateRequest, db=Depends(get_db)):
    try:
        course = course_dao.update_course(db, course_id, data)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 200, "message": "修改成功", "data": course}


@router.delete("/{course_id}", response_model=ApiResponse, summary="删除课程")
def delete_course(course_id: int, db=Depends(get_db)):
    try:
        course_dao.delete_course(db, course_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 200, "message": "删除成功", "data": []}


@router.get("/{course_id}", response_model=ApiResponse[CourseOut], summary="查询单个课程")
def query_course(course_id: int, db=Depends(get_db)):
    course = course_dao.get_course(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在或已删除")
    return {"code": 200, "message": "查询成功", "data": course}


@router.get("", response_model=ApiResponse[CourseListResponse], summary="分页查询课程")
def query_courses(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    class_id: int | None = Query(None, ge=1, description="按班级筛选"),
    subject_id: int | None = Query(None, ge=1, description="按科目筛选"),
    teacher_id: int | None = Query(None, ge=1, description="按授课老师筛选"),
    db=Depends(get_db),
):
    courses, total = course_dao.list_courses(db, page, size, class_id, subject_id, teacher_id)
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": courses}}

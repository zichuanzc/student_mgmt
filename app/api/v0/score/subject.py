# 负责路由：科目 subject

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.schemas.base import ApiResponse
from app.core.database import get_db
from app.dao import subject as subject_dao
from app.schemas.subject import (
    SubjectCreateRequest,
    SubjectListResponse,
    SubjectOut,
    SubjectUpdateRequest,
)


router = APIRouter(prefix="/subject", tags=["科目管理"])


@router.get("/{subject_id}", response_model=ApiResponse[SubjectOut], summary="查询单个科目")
def query_subject(subject_id: int=Path(), db=Depends(get_db)):
    subject = subject_dao.get_subject(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="科目不存在或已删除")
    return {"code": 200, "message": "查询成功", "data": subject}

@router.get("", response_model=ApiResponse[SubjectListResponse], summary="分页查询科目")
def query_subjects(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, max_length=25, description="按科目名称模糊搜索"),
    db=Depends(get_db),
):
    subjects, total = subject_dao.list_subjects(db, page, size, keyword)
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": subjects}}

@router.post("", response_model=ApiResponse[SubjectOut], summary="新增科目", status_code=201)
def create_subject(data: SubjectCreateRequest, db=Depends(get_db)):
    try:
        subject = subject_dao.create_subject(db, data)
    except ValueError as e:  # 编号重复等业务校验失败
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 201, "message": "创建成功", "data": subject}


@router.put("/{subject_id}", response_model=ApiResponse[SubjectOut], summary="修改科目")
def update_subject(subject_id: int, data: SubjectUpdateRequest, db=Depends(get_db)):
    try:
        subject = subject_dao.update_subject(db, subject_id, data)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 200, "message": "修改成功", "data": subject}


@router.delete("/{subject_id}", response_model=ApiResponse, summary="删除科目")
def delete_subject(subject_id: int, db=Depends(get_db)):
    try:
        subject_dao.delete_subject(db, subject_id)
    except LookupError as e: #不存在/已删除
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:  # 仍被课程引用
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 200, "message": "删除成功", "data": []}







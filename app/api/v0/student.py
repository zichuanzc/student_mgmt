"""学生管理模块路由"""
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Form
from sqlalchemy.orm import Session
from app.dao.teacher import get_teacher_by_id_db
from app.core.database import get_db
from app.dao.student import (
    add_student,
    class_exists,
    get_student_by_id,
    get_student_page,
    logic_delete_student,
    update_student as dao_update_student,
)

from app.schemas.base import ApiResponse, PageResponse
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/student", tags=["学生管理模块"])

# 获取学生列表
# @router.get("/",response_model=ApiResponse[list[StudentOut]],summary="获取学生列表（支持多条件筛选）")
# def list_students(
#     stu_id: Optional[int] = Query(None, description="学生编号"),
#     stu_name: Optional[str] = Query(None, description="学生姓名（模糊查询）"),
#     class_id: Optional[int] = Query(None, description="班级ID"),
#     db: Session = Depends(get_db),
# ):
#     """按学生编号、姓名、班级组合筛选，已逻辑删除的学生不会返回"""
#     return {"code":200, "message":"查询成功", "data": get_student_list(db, stu_id, stu_name, class_id)}

@router.get("/", response_model=ApiResponse[PageResponse[StudentOut]], summary="获取学生列表（支持多条件筛选+分页）")
def list_students(
    stu_id: Optional[int] = Query(None, description="学生编号"),
    stu_name: Optional[str] = Query(None, description="学生姓名（模糊查询）"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数，范围1~100"),
    db: Session = Depends(get_db),
):
    """按学生编号、姓名、班级组合筛选，已逻辑删除的学生不会返回"""
    page_result = get_student_page(db, stu_id, stu_name, class_id, page, size)
    return {"code": 200, "message": "查询成功", "data": page_result}


# 创建学生
@router.post("/",response_model=ApiResponse[StudentOut],status_code=201,summary="创建学生")
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    """新增学生：校验所属班级存在"""
    if not class_exists(db, payload.class_id):
        raise HTTPException(status_code=400, detail="所属班级不存在")
    if not get_teacher_by_id_db(db, payload.consultant_id):
        raise HTTPException(status_code=400, detail="所属顾问不存在")

    return {"code":201, "message":"创建成功", "data":add_student(db, payload)}

# 查询单个学生
@router.get("/{stu_id}",response_model=ApiResponse[StudentOut],summary="获取指定学生信息")
def get_student(stu_id: int=Path(...,ge=1), db: Session = Depends(get_db)):
    stu = get_student_by_id(db, stu_id)
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在或已被删除")
    return {"code":201, "message":"创建成功", "data":stu}

# 更新学生信息
@router.put("/{stu_id}",response_model=ApiResponse[StudentOut],summary="更新学生信息")
def update_student(stu_id: int, payload: Annotated[StudentUpdate, Form()], db: Session = Depends(get_db)):
    """局部更新学生信息；若修改班级则校验新班级是否存在"""
    stu = get_student_by_id(db, stu_id)
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在或已被删除")

    data = payload.model_dump(exclude_unset=True, exclude_none=True)

    if "class_id" in data and not class_exists(db, data["class_id"]):
        raise HTTPException(status_code=400, detail="所属班级不存在")
    if "consultant_id" in data and not get_teacher_by_id_db(db, data["consultant_id"]):
        raise HTTPException(status_code=400, detail="所属顾问不存在")
    return {"code":201, "message":"创建成功", "data":dao_update_student(db, stu, payload)}

# 逻辑删除学生
@router.delete("/{stu_id}", response_model=ApiResponse, summary="逻辑删除学生")
def delete_student(stu_id: int, db: Session = Depends(get_db)):
    """逻辑删除：仅把 is_deleted 置为 1"""
    stu = get_student_by_id(db, stu_id)
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在或已被删除")
    logic_delete_student(db, stu)
    return {"code": 200, "message": f"学生 {stu_id} 已逻辑删除", "data":[]}

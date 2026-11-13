from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException,Path,Query
# APIRouter（路由分组器）、Depends（依赖注入声明）、HTTPException（HTTP 异常类），是编写路由层代码的标配导入
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.base import ApiResponse
# database是一个模块，get_db:函数，它是 FastAPI 的数据库会话依赖
from app.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentOut, EmploymentListOut
from app.dao.employment import create_employment,get_employment_by_stu_id,list_employments_by_class,update_employment_by_stu_id
from app.dao import employment as dao


# APIRouter 作用：把一组相关的路由打包，再统一注册到 FastAPI 应用，实现模块化管理
router = APIRouter(
    prefix="/employment",      # 路径前缀，关键字参数，作用：所有路由自动加前缀
    tags=["就业管理模块"],       # tags:关键字参数，Swagger 文档分组标签;["学生就业管理"],列表类型，可传多个标签
    responses={404:{"description":"Not Found"}}
)

# 1、新增学生就业信息(自动读取学生及班级信息)
@router.post("/students/{stu_id}", response_model=ApiResponse[EmploymentOut], summary="新增学生就业信息")
def add_student_employment(
        stu_id: int,
        db: Session = Depends(get_db)
):
    # ① 判断学生是否存在
    student = dao.get_student_by_id(db, stu_id)
    if student is None:
        raise HTTPException(status_code=400, detail="未找到该学生信息")

    # ② 判断该学生是否已有就业记录
    existing = dao.get_employment_by_stu_id(db, stu_id)
    if existing is not None:
        raise HTTPException(status_code=400, detail="该学生已存在就业记录，请使用修改接口")

    # ③ 判断班级是否存在
    cls = dao.get_class_by_id(db, student.class_id)
    if cls is None:
        raise HTTPException(status_code=400, detail="未找到该学生所在的班级信息")

    # ④ 判断班级是否结课
    if cls.end_time is None:
        raise HTTPException(status_code=400, detail="该学生所在班级尚未结课，无法录入就业信息")

    # ⑤ 插入就业记录
    db_employment = dao.create_employment(db, student, cls)

    # ⑥ 返回统一格式
    return {"code": 200, "message": "新增成功", "data": db_employment}

# 2. 按学生编号查询就业信息（匹配需求文档端点）
@router.get("/students/{stu_id}", response_model=ApiResponse[EmploymentOut], summary="按学生编号查询就业信息")
def get_student_employment(stu_id: int, db: Session = Depends(get_db)):
    employment = dao.get_employment_by_stu_id(db, stu_id)
    # print(stu_id, type(stu_id))
    if not employment:
        raise HTTPException(status_code=404, detail="未找到该学生的就业信息")
    return {"code": 200, "message": "查询成功", "data": employment}

# 3. 按班级查询就业信息（匹配需求文档端点）
@router.get("/class/{class_code}", response_model=ApiResponse[EmploymentListOut], summary="按班级查询就业信息（分页）")
def get_class_employments(
    class_code: int = Path(..., ge=1),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    result = dao.list_employments_by_class(db, class_code, page, page_size)
    if result is None:
        raise HTTPException(status_code=404, detail="该班级不存在")
    total, items = result
    pages = (total + page_size - 1) // page_size if total else 0
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "items": items,
    }
    return {"code": 200, "message": "查询成功", "data": data}

# 4.按公司名称查询就业信息
@router.get("/company", response_model=ApiResponse[EmploymentListOut], summary="按公司名称查询就业信息（分页）")
def list_employment_by_company(
    company: str = Query(..., min_length=1, description="公司名称关键字（模糊匹配）"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    db: Session = Depends(get_db),
):
    total, items = dao.list_by_company(db, company, page, page_size)
    pages = (total + page_size - 1) // page_size if total else 0
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "items": items,
    }
    return {"code": 200, "message": "查询成功" if total else "暂无匹配记录", "data": data}

# 5.按薪资范围查询就业信息
@router.get("/salary_range", response_model=ApiResponse[EmploymentListOut], summary="按薪资范围查询就业信息（分页）")
def list_employment_by_salary(
    salary_min: float = Query(None, ge=0, description="薪资下限（含）"),
    salary_max: float = Query(None, ge=0, description="薪资上限（含）"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，1-100"),
    db: Session = Depends(get_db),
):
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise HTTPException(status_code=400, detail="salary_min 不能大于 salary_max")

    total, items = dao.list_by_salary_range(db, salary_min, salary_max, page, page_size)
    pages = (total + page_size - 1) // page_size if total else 0
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "items": items,
    }
    return {"code": 200, "message": "查询成功" if total else "该薪资区间无匹配记录", "data": data}

# 6. 修改就业信息
@router.put("/students/{stu_id}", response_model=ApiResponse[EmploymentOut], summary="修改就业信息")
def update_employment(
        stu_id: int = Path(..., ge=1, description="学生编号"),
        # 4个可选参数全部作为 Query 参数
        company: Optional[str] = Query(None, description="公司名称"),
        salary: Optional[float] = Query(None, description="薪资"),
        open_time: Optional[datetime] = Query(None, description="就业开放时间"),
        offer_time: Optional[datetime] = Query(None, description="Offer下发时间"),
        db: Session = Depends(get_db)
):
    # 将 stu_id 和这 4 个参数直接传给 DAO
    updated = dao.update_employment_by_stu_id(
        db, stu_id, company, salary, open_time, offer_time
    )

    if not updated:
        raise HTTPException(status_code=404, detail="就业记录不存在")

    return {"code": 200, "message": "修改成功", "data": updated}


# 7. 删除就业信息（逻辑删除）
@router.delete("/students/{stu_id}", summary="删除就业信息（逻辑删除）")
def delete_employment(stu_id: int, db: Session = Depends(get_db)):
    success = dao.delete_employment_by_stu_id(db, stu_id)
    if not success:
        raise HTTPException(status_code=404, detail="就业记录不存在")
    return {"code": 200, "message": "删除成功", "data": {}}




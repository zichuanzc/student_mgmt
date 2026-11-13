"""就业统计"""

from fastapi import APIRouter,Depends, HTTPException, Query
from app.core.database import get_db
from app.schemas.base import ApiResponse, TotalResponse
from app.schemas.statistic.employment import SalaryRankResponse, TimePerStudentResponse, TimePerClassResponse, AvgTimePerClassResponse
from app.dao.employment import get_top_salary, get_per_stu_time, get_per_class_time, get_per_class_avg_time
from app.lib.tools import get_specified_page



router=APIRouter(prefix="/employment", tags=["就业统计"])

@router.get('/rank', response_model=ApiResponse[TotalResponse[SalaryRankResponse]], summary="就业统计，返回薪资排名前n个学员的就业信息")
def get_emp_by_sal_rank(
    rank:int=Query(5, description="薪资排名"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    db=Depends(get_db)
):
    """返回前薪资前n名学生的就业信息，有很多数据时默认返回第一页"""
    rows = get_top_salary(db, rank)
    total, page = get_specified_page(rows, page, size)
    return {"code":200, "message":"查询成功", "data": {"total": total, "data": page}}

@router.get('/name', response_model=ApiResponse[TotalResponse[TimePerStudentResponse]], summary="就业统计，返回每个学生的就业时长，也可通过名字查单个学生")
def post_per_stu_emp_time(
        name:str=Query(None, description="学员姓名"),
        page: int = Query(1, ge=1, description="页码，从 1 开始"),
        size: int = Query(10, ge=1, le=100, description="每页条数"),
        db=Depends(get_db)
):
    rows = get_per_stu_time(db, name)
    if not rows:
        raise HTTPException(status_code=404, detail="所查询的学员不存在")
    total, page = get_specified_page(rows, page, size)
    return {"code": 200, "message": "查询成功", "data": {"total": total, "data": page}}

@router.get('/class_code', response_model=ApiResponse[TotalResponse[TimePerClassResponse]], summary="就业统计，通过班级编号，返回对应班级的所有学生的就业时长")
def post_per_class_emp_time(
        class_code:int=Query(None, description="班级编号"),
        page: int = Query(1, ge=1, description="页码，从 1 开始"),
        size: int = Query(10, ge=1, le=100, description="每页条数"),
        db=Depends(get_db)
):
    rows = get_per_class_time(db, class_code)
    if not rows:
        raise HTTPException(status_code=404, detail="所查询的班级不存在或尚未结课")
    total, page = get_specified_page(rows, page, size)
    return {"code": 200, "message": "查询成功", "data": {"total": total, "data": page}}


@router.get('/class_avg', response_model=ApiResponse[TotalResponse[AvgTimePerClassResponse]], summary="就业统计，返回所有班的平均就业时长，也可根据班级编号查看单个班级")
def post_per_class_emp_time(
        class_code:int=Query(None, description="班级编号"),
        page: int = Query(1, ge=1, description="页码，从 1 开始"),
        size: int = Query(10, ge=1, le=100, description="每页条数"),
        db=Depends(get_db)
):
    rows = get_per_class_avg_time(db, class_code)
    if not rows:
        raise HTTPException(status_code=404, detail="所查询的班级不存在或尚未结课")
    total, page = get_specified_page(rows, page, size)
    return {"code": 200, "message": "查询成功", "data": {"total": total, "data": page}}

from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dao.score import get_all_score_ge_target, get_fail_more_than_two, get_class_avg_score
from typing import Optional
from app.schemas.base import ApiResponse,PageResponse
from app.schemas.statistic.score import (StudentPassPassResponse,StudentFailScoreResponse,ClassExamAvgScoreResponse,
                                         StudentAllScorePassResponse,StudentFailManyResponse)


router = APIRouter(prefix="/score", tags=["成绩统计"])

@router.get("/score_all_ge", response_model=ApiResponse[PageResponse[StudentAllScorePassResponse]],
            summary="查询所有成绩都不低于达标分数线的学生,默认大于等于80")
async def all_ge(
        db: Session = Depends(get_db),
        min_target_score: Optional[int] = None,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量")
 ):
    # 参数校验：分数线 0~100
    if min_target_score is not None:
        if min_target_score < 0 or min_target_score > 100:
            raise HTTPException(status_code=400, detail="达标分数线范围必须在0~100之间")
    rows,total = get_all_score_ge_target(db,page, page_size,min_target_score)
    # return ApiResponse(
    #     code = 200,
    #     message = "查询成功",
    #     data ={
    # 'total': total,
    # 'page': page,
    # 'size': page_size,
    # 'data': rows
    #     }
    # )

    # 用一个字典，存学生编号、姓名、成绩列表

    stu_map = {}
    for r in rows:
        if r.stu_id not in stu_map:
            stu_map[r.stu_id] = {
                "name": r.name,
                "scores": []
            }
        stu_map[r.stu_id]["scores"].append(r.score)

    data = []
    for stu_id, info in stu_map.items():
        data.append(StudentAllScorePassResponse(
            stu_id=stu_id,
            name=info["name"],
            scores=info["scores"]
        ))
    return ApiResponse(
            code = 200,
            message = "查询成功",
            data ={
                'total': total,
                'page': page,
                'size': page_size,
                'data': data
                    }
        )

@router.get("/fail_more2", response_model=ApiResponse[PageResponse[StudentFailManyResponse]],
            summary="查询不及格次数达到指定数量的学生，默认及格线60，最少不及格2次")
async def fail_more2(db: Session = Depends(get_db),
                     pass_score: Optional[int] = None,
                     min_fail_count: Optional[int] = None,
                     page: int = Query(1, ge=1, description="页码"),
                     page_size: int = Query(10, ge=1, le=100, description="每页数量")
                     ):
    # ========= 参数校验 =========
    # 及格分数线：0~100
    if pass_score is not None:
        if pass_score < 0 or pass_score > 100:
            raise HTTPException(status_code=400, detail="及格分数线范围必须在0~100之间")
    # 最少不及格次数：不能小于1
    if min_fail_count is not None:
        if min_fail_count < 1:
            raise HTTPException(status_code=400, detail="最少不及格次数不能小于1")
    rows, total = get_fail_more_than_two(db,page, page_size,pass_score, min_fail_count)
    # return ApiResponse(
    #     code=200,
    #     message="查询成功",
    #     data={
    # 'total': total,
    # 'page': page,
    # 'size': page_size,
    # 'data': rows
    #     }
    # )

    # 用一个字典，存学生姓名、班级、不及格成绩列表
    stu_map = {}
    for r in rows:
        # 第一次遇到该学生，初始化信息
        if r.stu_id not in stu_map:
            stu_map[r.stu_id] = {
                "name": r.name,
                "class_code": r.class_code,
                "fail_scores": []
            }
        # 追加不及格分数
        stu_map[r.stu_id]["fail_scores"].append(r.score)

    data = []
    for stu_id, info in stu_map.items():
        data.append(StudentFailManyResponse(
            name=info["name"],
            class_code=info["class_code"],
            fail_scores=info["fail_scores"]
        ))

    return ApiResponse(code=200,
         message="查询成功",
         data={
        'total': total,
        'page': page,
        'size': page_size,
        'data': data
              }
                      )

@router.get("/class_avg", response_model=ApiResponse[PageResponse[ClassExamAvgScoreResponse]],summary="查询每个班级每场考试平均分，降序")
async def class_avg(db: Session = Depends(get_db),
                    page: int = Query(1, ge=1, description="页码"),
                    page_size: int = Query(10, ge=1, le=100, description="每页数量")
                    ):
    rows, total = get_class_avg_score(db,page, page_size)
    return ApiResponse(
        code=200,
        message="查询成功",
        data={
    'total': total,
    'page': page,
    'size': page_size,
    'data': rows
        }
    )
# 负责路由：成绩 score

from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.base import ApiResponse
from app.core.database import get_db
from app.dao import score as score_dao
from app.schemas.score import (
    ScoreByStudentUpdateRequest,
    ScoreCreateRequest,
    ScoreDeleteResponse,
    ScoreDetailListResponse,
    ScoreDetailOut,
    ScoreListResponse,
    ScoreOut,
)

router = APIRouter(prefix="/score", tags=["成绩管理"])


@router.post("", response_model=ApiResponse[ScoreOut], summary="录入成绩", status_code=201)
def create_score(data: ScoreCreateRequest, db=Depends(get_db)):
    try:
        score = score_dao.create_score(db, data)
    except ValueError as e:  # 学生/课程不存在、同批次重复录入
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 201, "message": "录入成功", "data": score}


@router.get("", response_model=ApiResponse[ScoreListResponse], summary="分页查询成绩")
def query_scores(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    stu_id: int | None = Query(None, ge=1, description="按学生筛选"),
    course_id: int | None = Query(None, ge=1, description="按课程筛选"),
    db=Depends(get_db),
):
    scores, total = score_dao.list_scores(db, page, size, stu_id, course_id)
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": scores}}


# ---------------------------------------------------------------------------
# 按学生 / 按老师 / 按科目 维度：都是多段路径，和分页列表 /score 互不冲突
# ---------------------------------------------------------------------------


@router.get("/student/{stu_id}", response_model=ApiResponse[ScoreDetailListResponse], summary="按学生 id 查询成绩")
def query_scores_by_student(
    stu_id: int,
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    db=Depends(get_db),
):
    """查这个学生所有课程的成绩，带出科目名、授课老师、班级编号"""
    try:
        items, total = score_dao.list_scores_by_student(db, stu_id, page, size)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": items}}


@router.put("/student/{stu_id}", response_model=ApiResponse[ScoreDetailOut], summary="按学生 id 修改成绩")
def update_score_by_student(stu_id: int, data: ScoreByStudentUpdateRequest, db=Depends(get_db)):
    """用「学生 + 课程 + 批次」定位一条成绩直接改分，前端不需要先查 score_id"""
    try:
        score = score_dao.update_score_by_student(db, stu_id, data.course_id, data.exam_order, data.score)
    except LookupError as e:  # 这条成绩还没录
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:  # 学生/课程不存在
        raise HTTPException(status_code=400, detail=str(e))
    # 改完回显明细，前端可以直接刷新那一行
    return {"code": 200, "message": "修改成功",
            "data": score_dao.get_score_detail(db, score.id)}


@router.get("/teacher/{teacher_id}", response_model=ApiResponse[ScoreDetailListResponse], summary="按老师 id 查询成绩")
def query_scores_by_teacher(
    teacher_id: int,
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    subject_id: int | None = Query(None, ge=1, description="按科目筛选（可选）"),
    db=Depends(get_db),
):
    """查这个老师所教课程下所有学生的成绩；课程被软删的不再出现"""
    try:
        items, total = score_dao.list_scores_by_teacher(db, teacher_id, page, size, subject_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": items}}


@router.get("/subject/{subject_id}", response_model=ApiResponse[ScoreDetailListResponse], summary="按科目 id 查询成绩")
def query_scores_by_subject(
    subject_id: int,
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    class_id: int | None = Query(None, ge=1, description="按班级筛选（可选）"),
    db=Depends(get_db),
):
    """查这个科目下所有班级、所有学生的成绩；科目被软删的返回 404"""
    try:
        items, total = score_dao.list_scores_by_subject(db, subject_id, page, size, class_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 200, "message": "查询成功",
            "data": {"total": total, "data": items}}


@router.delete("/student/{stu_id}", response_model=ApiResponse[ScoreDeleteResponse], summary="按学生 id 删除成绩")
def delete_scores_by_student(
    stu_id: int,
    course_id: int | None = Query(None, ge=1, description="只删这门课的成绩；不传则删该学生全部成绩"),
    exam_order: int | None = Query(None, ge=1, description="只删这个批次，必须同时传 course_id"),
    db=Depends(get_db),
):
    """逐级收窄：不带参数删全部 → 带 course_id 删该课 → 再加 exam_order 只删一条

    注意是软删除（is_deleted=1），数据仍在库里，可人工恢复。
    """
    try:
        deleted = score_dao.delete_scores_by_student(db, stu_id, course_id, exam_order)
    except LookupError as e:  # 学生不存在 / 没有可删的成绩
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:  # 参数组合不合法
        raise HTTPException(status_code=400, detail=str(e))
    return {"code": 200, "message": f"删除成功，共 {deleted} 条",
            "data": {"deleted": deleted}}

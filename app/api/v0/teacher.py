# from fastapi import APIRouter, Depends, Query, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.models.teacher import Teacher
# from app.schemas.teacher_schema import TeacherCreate, TeacherUpdate
#
# router=APIRouter(prefix="/teacher", tags=["老师管理"])
#
#
# # ================= 1. 获取老师列表（分页） =================
# @router.get("", summary="获取老师列表")
# def get_teachers(
#         page: int = Query(1, ge=1, description="页码"),
#         size: int = Query(10, ge=1, description="每页数量"),
#         db: Session = Depends(get_db)
# ):
#     skip = (page - 1) * size
#     # 只查询未删除的老师
#     query = db.query(Teacher).filter(Teacher.is_deleted == 0)
#     total = query.count()
#     teachers = query.offset(skip).limit(size).all()
#
#     return {
#         "code": 200,
#         "message": "获取成功",
#         "total": total,
#         "page": page,
#         "size": size,
#         "data": teachers
#     }
#
#
# # ================= 2. 新增老师 =================
# @router.post("", summary="新增老师")
# def create_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
#     # 检查教师编号是否重复（如果传了的话）
#     if teacher_in.teacher_code:
#         exist = db.query(Teacher).filter(Teacher.teacher_code == teacher_in.teacher_code).first()
#         if exist:
#             raise HTTPException(status_code=400, detail="教师编号已存在")
#
#     # 组装数据存入数据库
#     new_teacher = Teacher(
#         teacher_code=teacher_in.teacher_code,
#         name=teacher_in.name,
#         email=teacher_in.email,
#         is_head=teacher_in.is_head
#     )
#     db.add(new_teacher)
#     db.commit()
#     db.refresh(new_teacher)
#
#     return {"code": 200, "message": "新增成功", "data": new_teacher}
#
#
# # ================= 3. 修改老师信息 =================
# @router.put("/{teacher_id}", summary="修改老师")
# def update_teacher(teacher_id: int, teacher_in: TeacherUpdate, db: Session = Depends(get_db)):
#     db_teacher = db.query(Teacher) \
#                 .filter(Teacher.id == teacher_id, Teacher.is_deleted == 0) \
#                 .first()
#     if not db_teacher:
#         raise HTTPException(status_code=404, detail="老师不存在")
#
#     # 动态更新传了值的字段
#     update_data = teacher_in.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_teacher, key, value)
#
#     db.commit()
#     db.refresh(db_teacher)
#     return {"code": 200, "message": "修改成功", "data": db_teacher}
#
#
# # ================= 4. 软删除老师 =================
# @router.delete("/{teacher_id}", summary="删除老师")
# def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
#     db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id,
#                                                  Teacher.is_deleted == 0).first()
#     if not db_teacher:
#         raise HTTPException(status_code=404, detail="老师不存在")
#
#     # 软删除：把 is_deleted 改为 1
#     db_teacher.is_deleted = 1
#     db.commit()
#     return {"code": 200, "message": "删除成功"}



from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, HTTPException
from app.models.class_ import Class
from app.core.database import get_db
from app.dao import teacher as teacher_dao
from app.schemas.base import ApiResponse, PageResponse
from app.schemas.teacher_schema import TeacherCreate, TeacherUpdate, TeacherOut

router = APIRouter(prefix="/teacher", tags=["老师管理模块"])

# ================= 获取老师列表（分页） =================
@router.get("", response_model=ApiResponse[PageResponse[TeacherOut]], summary="获取老师列表")
def get_teachers(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, description="每页数量"),
        db: Session = Depends(get_db)
):
    # 调用 DAO
    total, teachers = teacher_dao.get_teachers_db(db, page, size)
    return {
        "code": 200,
        "message": "获取成功",
        "data":{
            "total": total,
            "page": page,
            "size": size,
            "data": teachers
        }
    }

# ================= 新增老师 =================
@router.post("", response_model=ApiResponse[TeacherOut], summary="新增老师")
def create_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    # 调 DAO
    if teacher_in.teacher_code:
        exist = teacher_dao.get_teacher_by_code_db(db, teacher_in.teacher_code)
        if exist:
            raise HTTPException(status_code=400, detail="教师编号已存在")
    # 存库（调 DAO）
    new_teacher = teacher_dao.create_teacher_db(db, teacher_in.model_dump())
    return {"code": 200, "message": "新增成功", "data": new_teacher}

# ================= 修改老师信息 =================
@router.put("/{teacher_id}", response_model=ApiResponse[TeacherOut], summary="修改老师")
def update_teacher(teacher_id: int, teacher_in: TeacherUpdate, db: Session = Depends(get_db)):
    # 调 DAO
    db_teacher = teacher_dao.get_teacher_by_id_db(db, teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="老师不存在")
    # 调 DAO
    update_data = teacher_in.model_dump(exclude_unset=True)
    updated_teacher = teacher_dao.update_teacher_db(db, db_teacher, update_data)
    return {"code": 200, "message": "修改成功", "data": updated_teacher}

# # ================= 4. 软删除老师 =================
# @router.delete("/{teacher_id}", response_model=ApiResponse[TeacherOut], summary="删除老师")
# def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
#     # 查老师是否存在（调 DAO）
#     db_teacher = teacher_dao.get_teacher_by_id_db(db, teacher_id)
#     if not db_teacher:
#         raise HTTPException(status_code=404, detail="老师不存在")
#     # 查老师是否担任班主任（调 DAO）
#     if teacher_dao.check_teacher_has_class(db, teacher_id):
#         raise HTTPException(status_code=400, detail="该老师还在担任班主任，请先调整班级")
#     # 软删除（调 DAO）
#     teacher_dao.delete_teacher_db(db, db_teacher)
#     return {"code": 200, "message": "删除成功", "data":db_teacher}
# ================= 软删除老师 =================
@router.delete("/{teacher_id}", response_model=ApiResponse[None], summary="删除老师")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    # 查老师是否存在
    db_teacher = teacher_dao.get_teacher_by_id_db(db, teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="老师不存在")

    # 在模块内部直接校验
    has_class = db.query(Class).filter(
        Class.teacher_id == teacher_id,
        Class.is_deleted == 0
    ).first()

    if has_class:
        raise HTTPException(status_code=400, detail="该老师还在担任班主任，请先更换班级班主任再删除！")

    #  执行软删除
    teacher_dao.delete_teacher_db(db, db_teacher)
    return {"code": 200, "message": "删除成功", "data": None}

# ================= 新增：根据教师编号查询老师 =================
@router.get("/code/{teacher_code}", response_model=ApiResponse[TeacherOut], summary="根据教师编号查询老师")
def get_teacher_by_code(teacher_code: int, db: Session = Depends(get_db)):
    # 调用 DAO 查询
    db_teacher = teacher_dao.get_teacher_by_code_only_db(db, teacher_code)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="不存在该老师")
    return {"code": 200, "message": "查询成功", "data": db_teacher}
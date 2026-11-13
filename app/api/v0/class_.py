# from fastapi import APIRouter, Depends, Query, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.models.class_ import Class
# from app.models.teacher import Teacher
# from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassOut
#
#
# router=APIRouter(prefix="/class", tags=["班级管理"])
#
#
# # ================= 1. 获取班级列表 =================
# @router.get("", summary="获取班级列表")
# def get_classes(
#         page: int = Query(1, ge=1, description="页码"),
#         size: int = Query(10, ge=1, description="每页数量"),
#         db: Session = Depends(get_db)
# ):
#     skip = (page - 1) * size
#     query = db.query(Class).filter(Class.is_deleted == 0)
#     total = query.count()
#     classes = query.offset(skip).limit(size).all()
#
#     return {
#         "code": 200,
#         "message": "获取成功",
#         "total": total,
#         "data": classes
#     }
#
#
# # ================= 2. 新增班级 =================
# @router.post("", summary="新增班级")
# def create_class(class_in: ClassCreate, db: Session = Depends(get_db)):
#     # 校验班主任是否存在
#     teacher = db.query(Teacher) \
#                .filter(Teacher.id == class_in.teacher_id,Teacher.is_deleted == 0) \
#                .first()
#     if not teacher:
#         raise HTTPException(status_code=400, detail="指定的班主任不存在")
#
#     new_class = Class(
#         class_code=class_in.class_code,
#         start_time=class_in.start_time,
#         end_time=class_in.end_time,
#         teacher_id=class_in.teacher_id
#     )
#     db.add(new_class)
#     db.commit()
#     db.refresh(new_class)
#
#     return {"code": 200, "message": "班级创建成功", "data": new_class}
#
#
# # ================= 3. 修改班级 =================
# @router.put("/{class_id}", summary="修改班级")
# def update_class(class_id: int, class_in: ClassUpdate, db: Session = Depends(get_db)):
#     db_class = db.query(Class).filter(Class.id == class_id, Class.is_deleted == 0).first()
#     if not db_class:
#         raise HTTPException(status_code=404, detail="班级不存在")
#
#     update_data = class_in.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_class, key, value)
#
#     db.commit()
#     db.refresh(db_class)
#     return {"code": 200, "message": "修改成功", "data": db_class}
#
#
# # ================= 4. 软删除班级 =================
# @router.delete("/{class_id}", summary="删除班级")
# def delete_class(class_id: int, db: Session = Depends(get_db)):
#     db_class = db.query(Class).filter(Class.id == class_id, Class.is_deleted == 0).first()
#     if not db_class:
#         raise HTTPException(status_code=404, detail="班级不存在")
#
#     db_class.is_deleted = 1
#     db.commit()
#     return {"code": 200, "message": "删除成功"}


from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.dao import class_ as class_dao
from app.schemas.base import ApiResponse
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassOut
from app.models.student import Student


router = APIRouter(prefix="/class", tags=["班级管理模块"])

# ================= 获取班级列表 =================
@router.get("", response_model=ApiResponse[list[ClassOut]], summary="获取班级列表")
def get_classes(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, description="每页数量"),
        db: Session = Depends(get_db)
):
    # 调用 DAO 层
    total, classes = class_dao.get_classes_db(db, page, size)
    return {
        "code": 200,
        "message": "获取成功",
        "data": classes
    }


# ================= ：根据班级编号查询 =================
@router.get("/code/{class_code}", response_model=ApiResponse[ClassOut] , summary="根据班级编号查询班级")
def get_class_by_code(class_code: int, db: Session = Depends(get_db)):
    # 调用 DAO 层查询
    db_class = class_dao.get_class_by_code_db(db, class_code)
    if not db_class:
        raise HTTPException(status_code=404, detail="不存在该班级")

    return {"code": 200, "message": "查询成功", "data": db_class}


# ================= 新增班级 =================
@router.post("",response_model=ApiResponse[ClassOut], summary="新增班级")
def create_class(class_in: ClassCreate, db: Session = Depends(get_db)):
    # 调用 DAO 校验老师
    teacher = class_dao.get_teacher_by_id_db(db, class_in.teacher_id)
    if not teacher:
        raise HTTPException(status_code=400, detail="指定的班主任不存在")

    # 调用 DAO 新增入库
    new_class = class_dao.create_class_db(db, class_in.model_dump())
    return {"code": 200, "message": "班级创建成功", "data": new_class}


# ================= 修改班级 =================
@router.put("/{class_id}", response_model=ApiResponse[ClassOut], summary="修改班级")
def update_class(class_id: int, class_in: ClassUpdate, db: Session = Depends(get_db)):
    db_class = class_dao.get_class_by_id_db(db, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="班级不存在")

    update_data = class_in.model_dump(exclude_unset=True)
    updated_class = class_dao.update_class_db(db, db_class, update_data)
    return {"code": 200, "message": "修改成功", "data": updated_class}


# ================= 软删除班级 =================
@router.delete("/{class_id}", response_model=ApiResponse[ClassOut], summary="删除班级")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    # 调用 DAO 查班级是否存在
    db_class = class_dao.get_class_by_id_db(db, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="班级不存在")
    has_student = db.query(Student).filter(
        Student.class_id == class_id,
        Student.is_deleted == 0
    ).first()

    if has_student:
        raise HTTPException(status_code=400, detail="该班级下还有在读学生，无法直接删除！请先转出学生。")
    # 调用 DAO 执行删除
    class_dao.delete_class_db(db, db_class)
    return {"code": 200, "message": "删除成功", "data":db_class}
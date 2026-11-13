"""学生模块数据库操作：student"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.class_ import Class
from app.schemas.base import PageResponse
from app.schemas.student import StudentCreate, StudentUpdate


# 查找学生列表
# def get_student_list(
#     db: Session,
#     stu_id: Optional[int] = None,
#     stu_name: Optional[str] = None,
#     class_id: Optional[int] = None,
# ) :                                 #参数可不传，默认是None
#     """多条件筛选学生：学生编号、姓名（模糊）、班级，自动过滤逻辑删除数据"""
#     q = db.query(Student).filter(Student.is_deleted == 0)  #去Student表取数据，只拿未删除的数据（is_deleted=1已删除）
#     if stu_id is not None:
#         # 学生表主键 id 就是学生编号
#         q = q.filter(Student.id == stu_id)
#     if stu_name:
#         q = q.filter(Student.name.like(f"%{stu_name}%"))
#     if class_id is not None:
#         q = q.filter(Student.class_id == class_id)
#     return q.order_by(Student.id).all()    #filter 只是叠加条件，all () 才查库,学生编号升序排序
# 查找学生列表
def get_student_page(
    db: Session,
    stu_id: Optional[int] = None,
    stu_name: Optional[str] = None,
    class_id: Optional[int] = None,
    page: int = 1,
    size: int = 10
):
    """多条件筛选学生 + 分页，自动过滤逻辑删除数据"""
    q = db.query(Student).filter(Student.is_deleted == 0)
    if stu_id is not None:
        q = q.filter(Student.id == stu_id)
    if stu_name:
        q = q.filter(Student.name.like(f"%{stu_name}%"))
    if class_id is not None:
        q = q.filter(Student.class_id == class_id)

    # 统计总数
    total = q.count()
    # 偏移量公式
    offset = (page - 1) * size
    records = q.order_by(Student.id).offset(offset).limit(size).all()

    # 返回和你PageResponse结构一模一样的字典
    return PageResponse(
        total=total,
        page=page,
        size=size,
        data=records
    )

# 根据ID查询单个学生
def get_student_by_id(db: Session, stu_id: int):
    """根据学生编号（主键 id）查询，自动过滤已逻辑删除的学生"""
    return (
        db.query(Student)
        .filter(Student.id == stu_id, Student.is_deleted == 0)
        .first()
    )

# """校验班级是否存在且未被删除"""
def class_exists(db: Session, class_id: int):
    return (
        db.query(Class)
        .filter(Class.id == class_id, Class.is_deleted == 0)
        .first()
        is not None
    )

# 新增学生
def add_student(db: Session, payload: StudentCreate):
    stu = Student(**payload.model_dump())  #把 Pydantic 模型转成字典,字典里的键值对，作为参数传给 `Student` 类
    db.add(stu)
    db.commit()
    db.refresh(stu)
    return stu

# ""更新学生：exclude_unset=True 只更新请求体中出现的字段"""
def update_student(db: Session, stu_obj: Student, payload: StudentUpdate):
    for k, v in payload.model_dump(exclude_unset=True).items():     #`exclude_unset`只排除前端没传的字段
        setattr(stu_obj, k, v)   #内置底层函数 setattr(stu_obj, 属性名, 值) 即  stu_obj.__dict__[key] = value
    db.commit()
    db.refresh(stu_obj)
    return stu_obj

# """逻辑删除：is_deleted 置 1，不物理删除数据"""
def logic_delete_student(db: Session, stu_obj: Student):

    stu_obj.is_deleted = 1
    db.commit()
    return stu_obj

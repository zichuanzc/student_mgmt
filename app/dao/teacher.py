"""负责操作数据库，增删改查：student"""

from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.models.class_ import Class

# 1. 获取老师列表（分页）
def get_teachers_db(db: Session, page: int, size: int):
    skip = (page - 1) * size
    query = db.query(Teacher).filter(Teacher.is_deleted == 0)
    total = query.count()
    teachers = query.offset(skip).limit(size).all()
    return total, teachers

# 2. 根据教师编号查重
def get_teacher_by_code_db(db: Session, teacher_code: int):
    return db.query(Teacher).filter(Teacher.teacher_code == teacher_code).first()

# 3. 新增老师
def create_teacher_db(db: Session, teacher_data: dict):
    new_teacher = Teacher(**teacher_data)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher

# 4. 根据 ID 查老师
def get_teacher_by_id_db(db: Session, teacher_id: int):
    return db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_deleted == 0
    ).first()

# 5. 修改老师
def update_teacher_db(db: Session, db_teacher: Teacher, update_data: dict):
    for key, value in update_data.items():
        setattr(db_teacher, key, value)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

# 6. 软删除老师
def delete_teacher_db(db: Session, db_teacher: Teacher):
    db_teacher.is_deleted = 1
    db.commit()
    return db_teacher

# ================= 7. 新增：根据教师编号（teacher_code）查询老师 =================
def get_teacher_by_code_only_db(db: Session, teacher_code: int):
    # 注意：这里只查未删除的老师
    return db.query(Teacher).filter(
        Teacher.teacher_code == teacher_code,
        Teacher.is_deleted == 0
    ).first()

# ================= 8. 新增：拦截 =================

def check_teacher_has_class(db: Session, teacher_id: int):
    # 查有没有未删除的班级在用这个老师
    return db.query(Class).filter(Class.teacher_id == teacher_id, Class.is_deleted == 0).first()
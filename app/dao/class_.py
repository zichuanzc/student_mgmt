"""负责操作数据库，增删改查：class_"""

from sqlalchemy.orm import Session
from app.models.class_ import Class
from app.models.teacher import Teacher

# ================= 1. 获取班级列表 =================
def get_classes_db(db: Session, page: int, size: int):
    skip = (page - 1) * size
    query = db.query(Class).filter(Class.is_deleted == 0)
    total = query.count()
    classes = query.offset(skip).limit(size).all()
    return total, classes

# ================= 2. 根据 ID 查老师 =================
def get_teacher_by_id_db(db: Session, teacher_id: int):
    return db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.is_deleted == 0
    ).first()

# ================= 3. 新增班级 =================
def create_class_db(db: Session, class_data: dict):
    new_class = Class(**class_data)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

# ================= 4. 根据 ID 查班级 =================
def get_class_by_id_db(db: Session, class_id: int):
    return db.query(Class).filter(
        Class.id == class_id,
        Class.is_deleted == 0
    ).first()

# ================= 5. 修改班级 =================
def update_class_db(db: Session, db_class: Class, update_data: dict):
    for key, value in update_data.items():
        setattr(db_class, key, value)
    db.commit()
    db.refresh(db_class)
    return db_class

# ================= 6. 软删除班级 =================
def delete_class_db(db: Session, db_class: Class):
    db_class.is_deleted = 1
    db.commit()
    return db_class

# ================= 7. 根据班级编号（class_code）查询班级 =================
def get_class_by_code_db(db: Session, class_code: int):
    return db.query(Class).filter(
        Class.class_code == class_code,
        Class.is_deleted == 0
    ).first()
"""负责操作数据库，增删改查：employment"""

from app.models.employment import Employment
from app.models.class_ import Class
from sqlalchemy import func, text


def get_top_salary(db,rank=5):
    """获取前几名薪资，默认前5名"""
    res = db.query(Employment.id,
                   Employment.student_id,
                   Employment.student_name,
                   Employment.class_code,
                   Employment.offer_time,
                   Employment.company,
                   Employment.salary) \
        .filter(Employment.is_deleted == 0, Employment.offer_time.isnot(None)) \
        .order_by(Employment.salary.desc()).offset(0).limit(rank).all()
    return res


def get_per_stu_time(db, name=None):
    """获取每个学生的就业时长，也可通过名字查询学生的就业时长，支持模糊查询"""
    if name:
        res = db.query(Employment.id,
                       Employment.student_id,
                       Employment.student_name,
                       Employment.class_code,
                       Employment.offer_time,
                       func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0, Employment.student_name.ilike(f"%{name}%")).all()
    else:
        res = db.query(Employment.id,
                       Employment.student_id,
                       Employment.student_name,
                       Employment.class_code,
                       Employment.offer_time,
                       func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0).all()
    return res

def get_per_class_time(db, class_code=None):
    """根据班级编号获取某个班级的所有学员就业时长，class_code为None时返回班级编号最大的班级的对应信息"""
    if class_code:
        res = db.query(Employment.id,
                       Employment.student_id,
                       Employment.student_name,
                       Employment.class_code,
                       Employment.offer_time,
                       func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0, Employment.class_code==class_code).all()
    else:
        max_class = db.query(Class.class_code).order_by(Class.class_code.desc()).first()
        # print(max_class)
        print(max_class.class_code)
        res = db.query(Employment.id,
                       Employment.student_id,
                       Employment.student_name,
                       Employment.class_code,
                       Employment.offer_time,
                       func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0, Employment.class_code==max_class.class_code).all()
    return res


def get_per_class_avg_time(db, class_code=None):
    """获取每个班级的平均就业时长，也可根据班级编号查看指定班级"""
    if class_code:
        res = db.query(Employment.class_code,
                       func.avg(func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time)).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0, Employment.class_code==class_code, Employment.open_time.isnot(None)) \
            .group_by(Employment.class_code) \
            .order_by(Employment.class_code).all()
    else:
        res = db.query(Employment.class_code,
                       func.avg(func.timestampdiff(text("SECOND"), Employment.open_time, Employment.offer_time)).label("emp_seconds")) \
            .filter(Employment.is_deleted == 0, Employment.open_time.isnot(None)) \
            .group_by(Employment.class_code) \
            .order_by(Employment.class_code).all()
    return res


# DAO 全称 Data Access Object（数据访问对象），专门封装所有数据库操作，和路由层分离
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.employment import Employment
from app.schemas.employment import EmploymentCreate, EmploymentUpdate
from datetime import datetime
from typing import Optional, List, Tuple
# Session：数据库会话类型，用于类型提示

# 1、新增学生就业信息
# 函数定义，参数是数据库会话和学生编号，返回「数据 + 提示信息」的元组。
def get_student_by_id(db: Session, student_id: int):
    return db.query(Student).filter(
        Student.id == student_id,
        Student.is_deleted == 0,
    ).first()

def get_class_by_id(db: Session, class_id: int):
    return db.query(Class).filter(
        Class.id == class_id,
        Class.is_deleted == 0,
    ).first()

def create_employment(db: Session, student: Student, cls: Class):
    db_employment = Employment(
        student_id=student.id,
        student_name=student.name,
        class_code=cls.class_code,
        # 其余字段默认 None
    )
    db.add(db_employment)
    db.commit()
    db.refresh(db_employment)
    return db_employment

# 2. 按主键ID查询单条就业记录
def get_employment_by_id(db: Session, employment_id: int):
    return db.query(Employment).filter(
        Employment.id == employment_id,
        Employment.is_deleted == 0  # 默认过滤已删除数据
    ).first()

# 3. 按学生编号查询就业信息（对应需求GET /employment/students/{id}）
def get_employment_by_stu_id(db: Session, student_id: int):
    return db.query(Employment).filter(
        Employment.student_id == student_id,
        Employment.is_deleted == 0
    ).first()

# 4. 按班级查询所有学生就业信息
def list_employments_by_class(db: Session, class_code: int, page: int = 1, page_size: int = 10):
    class_exists = db.query(Class).filter(
        Class.class_code == class_code,
        Class.is_deleted == 0
    ).first()
    if not class_exists:
        return None

    query = db.query(Employment).filter(
        Employment.class_code == class_code,
        Employment.is_deleted == 0
    ).order_by(Employment.id.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items

# 5.按公司名称查询就业信息
def list_by_company(
    db: Session,
    company: str,
    page: int = 1,
    page_size: int = 10,
):
    base_query = db.query(Employment).filter(Employment.is_deleted == 0)
    if company:
        base_query = base_query.filter(Employment.company.like(f"%{company}%"))

    total = base_query.count()
    items = (
        base_query
        .order_by(Employment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items

# 6.按薪资范围查询就业信息
def list_by_salary_range(
    db: Session,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    page: int = 1,
    page_size: int = 10,
):
    base_query = db.query(Employment).filter(Employment.is_deleted == 0)
    if salary_min is not None:
        base_query = base_query.filter(Employment.salary >= salary_min)
    if salary_max is not None:
        base_query = base_query.filter(Employment.salary <= salary_max)

    total = base_query.count()
    items = (
        base_query
        .order_by(Employment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


# 7. 修改就业信息（对应需求3：部分更新）
def update_employment_by_stu_id(
        db: Session,
        student_id: int,
        company: Optional[str] = None,
        salary: Optional[float] = None,
        open_time: Optional[datetime] = None,
        offer_time: Optional[datetime] = None
):
    # ① 按学生编号查记录
    db_employment = get_employment_by_stu_id(db, student_id)
    if db_employment is None:
        return None

    # ② 标记是否发生了字段修改
    has_changed = False

    # ③ 谁不是 None，就改谁（不传就是 None，直接跳过，不覆盖原值）
    if company is not None:
        db_employment.company = company
        has_changed = True

    if salary is not None:
        db_employment.salary = salary
        has_changed = True

    if open_time is not None:
        db_employment.open_time = open_time
        has_changed = True

    if offer_time is not None:
        db_employment.offer_time = offer_time
        has_changed = True

    # ④ 如果确实有修改，才执行 commit
    if has_changed:
        db.commit()
        db.refresh(db_employment)

    return db_employment


# 8. 删除就业信息（对应需求3：逻辑删除）
def delete_employment_by_stu_id(db: Session, student_id: int):
    db_employment = get_employment_by_stu_id(db, student_id)
    if not db_employment:
        return False

    # 不物理删除，只标记为已删除，保留历史数据用于统计
    db_employment.is_deleted = True
    db_employment.update_time = datetime.now()
    db.commit()
    return True
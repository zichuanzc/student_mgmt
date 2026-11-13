from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.student import Student
from app.models.class_ import Class
from typing import Optional

def get_student_older(db: Session, page, page_size,age_threshold: Optional[int] = None, ):
    """
    查询超过指定年龄的学员信息
    :param age_threshold: 年龄阈值，不传则返回全部学员
    :param page: 页码
    :param page_size: 每页条数
    :return: rows, total
    """
    q = db.query(Student).filter(Student.is_deleted == 0)
    if age_threshold is not None:
        q = q.filter(Student.age > age_threshold)
    # 先查总数
    total = q.count()
    # 分页
    offset = (page - 1) * page_size
    q = q.order_by(Student.id)
    rows = q.offset(offset).limit(page_size).all()
    return rows, total

def get_class_gender_stat(db: Session, page, page_size):
    """统计每个班级总人数、男生、女生人数（带分页）"""

    # 子查询：先完成各班人数、性别统计（聚合）
    stat_sub = db.query(
        Class.id.label("class_id"),
        Class.class_code,
        func.count(Student.id).label("total"),
        func.sum(case((Student.gender == "男", 1), else_=0)).label("male_cnt"),
        func.sum(case((Student.gender == "女", 1), else_=0)).label("female_cnt")
    ).join(Student, Student.class_id == Class.id) \
    .filter(Student.is_deleted == 0, Class.is_deleted == 0) \
    .group_by(Class.id, Class.class_code).subquery()

    # 统计符合条件的班级总数量
    total = db.query(func.count(stat_sub.c.class_id)).scalar() or 0

    # 对聚合好的班级结果分页，按class_id排序，防止翻页乱序
    res = db.query(
        stat_sub.c.class_id,
        stat_sub.c.class_code,
        stat_sub.c.total,
        stat_sub.c.male_cnt,
        stat_sub.c.female_cnt
    ).order_by(stat_sub.c.class_id) \
     .offset((page - 1) * page_size) \
     .limit(page_size) \
     .all()

    return res, total
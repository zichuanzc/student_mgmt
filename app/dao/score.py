# 负责操作数据库，增删改查：score
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.class_ import Class
from app.models.course import Course
from app.models.score import Score
from app.models.student import Student
from app.models.subject import Subject
from app.models.teacher import Teacher





def list_scores(db, page, size, stu_id=None, course_id=None):
    q = db.query(Score).filter(Score.is_deleted == 0)
    if stu_id is not None:
        q = q.filter(Score.stu_id == stu_id)
    if course_id is not None:
        q = q.filter(Score.course_id == course_id)
    total = q.count()
    rows = q.order_by(Score.id).offset((page - 1) * size).limit(size).all()
    return rows, total


def _check_refs(db, stu_id=None, course_id=None):
    """成绩必须挂在真实存在的学生和课程上，否则就是脏数据"""
    if stu_id is not None:
        exists = db.query(Student.id).filter(Student.id == stu_id, Student.is_deleted == 0).first()
        if not exists:
            raise ValueError(f"学生 {stu_id} 不存在或已删除")
    if course_id is not None:
        exists = db.query(Course.id).filter(Course.id == course_id, Course.is_deleted == 0).first()
        if not exists:
            raise ValueError(f"课程 {course_id} 不存在或已删除")


def _check_duplicate(db, stu_id, course_id, exam_order):
    """同一学生 + 同一课程 + 同一批次只能有一条成绩"""
    q = db.query(Score).filter(
        Score.stu_id == stu_id,
        Score.course_id == course_id,
        Score.is_deleted == 0,
    )
    if exam_order is None:
        q = q.filter(Score.exam_order.is_(None))
    else:
        q = q.filter(Score.exam_order == exam_order)
    if q.first():
        raise ValueError("该学生在这门课的这个批次已经录过成绩了，请改用 PUT /score/student/{stu_id} 修改")


def create_score(db, data):
    _check_refs(db, data.stu_id, data.course_id)
    _check_duplicate(db, data.stu_id, data.course_id, data.exam_order)

    score = Score(**data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


# ---------------------------------------------------------------------------
# 以下是"按学生 / 按老师 / 按科目"查询与修改成绩用的联表查询
# ---------------------------------------------------------------------------


def _detail_query(db):
    """成绩明细的公共查询：score 往四个方向联表，把姓名、科目名、班级编号一起取出来

    关联路径：score → student
                     → course → subject
                              → teacher
                              → class_
    score 对 course 是多对一，联表不会放大行数，所以可以直接 count()。
    """
    return (
        db.query(
            Score.id.label("id"),
            Score.stu_id.label("stu_id"),
            Student.name.label("student_name"),
            Class.class_code.label("class_code"),
            Score.course_id.label("course_id"),
            Subject.id.label("subject_id"),
            Subject.subject_name.label("subject_name"),
            Teacher.id.label("teacher_id"),
            Teacher.name.label("teacher_name"),
            Score.score.label("score"),
            Score.exam_order.label("exam_order"),
        )
        .join(Student, Student.id == Score.stu_id)
        .join(Course, Course.id == Score.course_id)
        .join(Subject, Subject.id == Course.subject_id)
        .join(Teacher, Teacher.id == Course.teacher_id)
        .join(Class, Class.id == Course.class_id)
        .filter(Score.is_deleted == 0)
    )


def _rows_to_dicts(rows):
    """把 SQLAlchemy 的 Row 转成普通 dict，Pydantic 用 dict 校验最省事"""
    return [dict(row._mapping) for row in rows]


def list_scores_by_student(db, stu_id, page, size):
    """按学生 id 查他所有课程的成绩

    注意：多个条件用 filter 逗号分隔是 AND；
    .count() 必须在 offset/limit 之前，才能拿到总条数。
    """
    exists = db.query(Student.id).filter(Student.id == stu_id, Student.is_deleted == 0).first()
    if not exists:
        raise LookupError(f"学生 {stu_id} 不存在或已删除")

    q = _detail_query(db).filter(Score.stu_id == stu_id)
    total = q.count()
    rows = (
        q.order_by(Score.course_id, Score.exam_order, Score.id)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return _rows_to_dicts(rows), total


def list_scores_by_teacher(db, teacher_id, page, size, subject_id=None):
    """按老师 id 查他所教课程下的所有学生成绩

    过滤条件落在 course.teacher_id 上，而不是 score 表 —— 成绩表本身没有老师字段，
    "这门课是谁教的"这个信息存在 course 里。
    已删除的课程不再出现在老师的成绩列表里（Course.is_deleted == 0）。
    """
    exists = db.query(Teacher.id).filter(Teacher.id == teacher_id, Teacher.is_deleted == 0).first()
    if not exists:
        raise LookupError(f"老师 {teacher_id} 不存在或已删除")

    q = _detail_query(db).filter(Course.teacher_id == teacher_id, Course.is_deleted == 0)
    if subject_id is not None:
        q = q.filter(Course.subject_id == subject_id)
    total = q.count()
    rows = (
        q.order_by(Score.course_id, Score.stu_id, Score.exam_order)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return _rows_to_dicts(rows), total


def get_score_detail(db, score_id):
    """单条成绩的明细，供"改完立刻回显"用"""
    row = _detail_query(db).filter(Score.id == score_id).first()
    return dict(row._mapping) if row else None


def list_scores_by_subject(db, subject_id, page, size, class_id=None):
    """按科目 id 查成绩：该科目下所有班级、所有学生的成绩

    科目信息不在 score 表里，要先经过 course 中转，
    所以条件落在 Course.subject_id 上，而不是 Score 上。
    """
    exists = db.query(Subject.id).filter(Subject.id == subject_id, Subject.is_deleted == 0).first()
    if not exists:
        raise LookupError(f"科目 {subject_id} 不存在或已删除")

    q = _detail_query(db).filter(Course.subject_id == subject_id, Course.is_deleted == 0)
    if class_id is not None:
        q = q.filter(Course.class_id == class_id)
    total = q.count()
    rows = (
        q.order_by(Score.course_id, Score.stu_id, Score.exam_order)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return _rows_to_dicts(rows), total


def delete_scores_by_student(db, stu_id, course_id=None, exam_order=None):
    """按学生 id 删成绩，可逐级收窄删除范围

    - 只传 stu_id                  → 删这个学生的全部成绩
    - stu_id + course_id           → 只删这门课的全部批次
    - stu_id + course_id + exam_order → 只删这一条

    用 Query.update() 做批量更新，一条 UPDATE 语句搞定，
    不会把对象逐个查出来再改（软删除仍然是 UPDATE，不是物理删除）。
    """
    exists = db.query(Student.id).filter(Student.id == stu_id, Student.is_deleted == 0).first()
    if not exists:
        raise LookupError(f"学生 {stu_id} 不存在或已删除")
    if exam_order is not None and course_id is None:
        raise ValueError("按批次删除时必须同时指定 course_id")

    q = db.query(Score).filter(Score.stu_id == stu_id, Score.is_deleted == 0)
    if course_id is not None:
        q = q.filter(Score.course_id == course_id)
        if exam_order is not None:
            q = q.filter(Score.exam_order == exam_order)

    # synchronize_session=False：不把已加载的对象同步到会话，批量场景更快
    deleted = q.update({Score.is_deleted: 1}, synchronize_session=False)
    if deleted == 0:
        db.rollback()
        raise LookupError("没有找到符合条件的成绩，可能已经被删过了")

    db.commit()
    return deleted



def get_score_by_student_course(db, stu_id, course_id, exam_order=None):
    """按 学生 + 课程 + 批次 定位成绩，不需要 score_id

    exam_order 为 None 时要匹配 exam_order IS NULL 的那条，
    所以这里必须写成 is_(None)，不能写 == None。
    """
    q = db.query(Score).filter(
        Score.stu_id == stu_id,
        Score.course_id == course_id,
        Score.is_deleted == 0,
    )
    if exam_order is None:
        q = q.filter(Score.exam_order.is_(None))
    else:
        q = q.filter(Score.exam_order == exam_order)
    return q.first()


def update_score_by_student(db, stu_id, course_id, exam_order, new_score):
    """按学生 id 改分：先校验学生/课程存在，再按三元组定位记录

    定位不到抛 LookupError（404），意味着"这条成绩还没录"，
    而不是"参数写错了"——所以和 ValueError 区分开。
    """
    _check_refs(db, stu_id, course_id)

    score = get_score_by_student_course(db, stu_id, course_id, exam_order)
    if score is None:
        raise LookupError("该学生这门课的这个批次还没有成绩，请先录入")

    score.score = new_score
    db.commit()
    db.refresh(score)
    return score






#成绩分析统计dao层
def get_all_score_ge_target(
    db: Session,
    page,
    page_size,
    min_target_score: Optional[int] = None

):
    """
    查询【所有考试成绩都大于等于指定达标分数线】的学生
    :param min_target_score: 达标分数线，不传默认80，学生每一门成绩都必须≥该分数才会被筛选出来
    :return: rows, total
    """
    if min_target_score is None:
        min_target_score = 80
    # 子查询：筛选满足条件的学生id（该学生最低分≥达标线）
    stu_sub = db.query(
        Score.stu_id
    ).filter(Score.is_deleted == 0) \
     .group_by(Score.stu_id) \
     .having(func.min(Score.score) >= min_target_score).subquery()

    # 符合条件的学生总数量
    total = db.query(func.count(stu_sub.c.stu_id)).scalar() or 0

    # 分页取学生id（按学生id排序，保证翻页稳定）
    page_stu_ids = db.query(stu_sub.c.stu_id)\
        .order_by(stu_sub.c.stu_id)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    page_stu_ids = [item[0] for item in page_stu_ids]
    if not page_stu_ids:
        return [], total

    # 根据这一页学生id，批量查询学生信息 + 成绩明细
    rows = db.query(
        Student.id.label("stu_id"),
        Student.name,
        Score.score
    ).join(Score, Student.id == Score.stu_id) \
     .filter(
        Student.id.in_(page_stu_ids),
        Student.is_deleted == 0,
        Score.is_deleted == 0
     ) \
     .order_by(Student.id, Score.id) \
     .all()

    return rows, total

def get_fail_more_than_two(
    db: Session,
    page,
    page_size,
    pass_score: Optional[int] = None,
    min_fail_count: Optional[int] = None

):
    """
    查询【不及格次数达到指定数量】的学生
    :param pass_score: 及格分数线，分数低于该值就算不及格，不传默认60
    :param min_fail_count: 需要满足的最少不及格次数，不传默认2
    :return: rows, total
    """
    if pass_score is None:
        pass_score = 60
    if min_fail_count is None:
        min_fail_count = 2

    # 子查询：筛选不及格次数达标的学生id
    stu_sub = db.query(
        Score.stu_id
    ).filter(
        Score.score < pass_score,
        Score.is_deleted == 0
    ) \
     .group_by(Score.stu_id) \
     .having(func.count(Score.id) >= min_fail_count).subquery()

    # 符合条件的学生总数
    total = db.query(func.count(stu_sub.c.stu_id)).scalar() or 0

    # 分页取学生id
    page_stu_ids = db.query(stu_sub.c.stu_id)\
        .order_by(stu_sub.c.stu_id)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    page_stu_ids = [item[0] for item in page_stu_ids]
    if not page_stu_ids:
        return [], total

    # 批量查询学生、班级、不及格成绩
    rows = db.query(
        Student.id.label("stu_id"),
        Student.name,
        Class.class_code,
        Score.score
    ).join(Class, Student.class_id == Class.id)\
     .join(Score, Student.id == Score.stu_id) \
     .filter(
        Student.id.in_(page_stu_ids),
        Score.score < pass_score,
        Student.is_deleted == 0,
        Class.is_deleted == 0,
        Score.is_deleted == 0
     ) \
     .order_by(Student.id, Score.id) \
     .all()

    return rows, total

def get_class_avg_score(
    db: Session,
    page,
    page_size
):
    """
    查询每个班级每一场考试的平均分，结果按平均分降序排列
    返回：班级id、班级编码、考试场次、平均分（保留2位小数）
    """

    # 学生表相当于中间桥梁，让分数表和班级表进行连接，取班级表里面的信息
    q = db.query(
        Class.id.label("class_id"),
        Class.class_code,
        Score.exam_order,
        func.round(func.avg(Score.score), 2).label("avg_score")
    ).join(Student, Score.stu_id == Student.id) \
     .join(Class, Student.class_id == Class.id) \
     .filter(
         Student.is_deleted == 0,
         Class.is_deleted == 0,
         Score.is_deleted == 0
     ) \
     .group_by(Class.id, Class.class_code, Score.exam_order) \
     .order_by(func.avg(Score.score).desc(), Class.id, Score.exam_order)

    total = q.count()
    offset = (page - 1) * page_size
    rows = q.offset(offset).limit(page_size).all()
    return rows, total

# 负责操作数据库，增删改查：course

from app.models.class_ import Class
from app.models.course import Course
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.score import Score

def _get_alive(db, course_id):
    return db.query(Course).filter(Course.id == course_id, Course.is_deleted == 0).first()


def get_course(db, course_id):
    return _get_alive(db, course_id)


def list_courses(db, page, size, class_id=None, subject_id=None, teacher_id=None):
    q = db.query(Course).filter(Course.is_deleted == 0)
    if class_id is not None:
        q = q.filter(Course.class_id == class_id)
    if subject_id is not None:
        q = q.filter(Course.subject_id == subject_id)
    if teacher_id is not None:
        q = q.filter(Course.teacher_id == teacher_id)
    total = q.count()
    rows = q.order_by(Course.id).offset((page - 1) * size).limit(size).all()
    return rows, total


def _check_refs(db, class_id=None, subject_id=None, teacher_id=None):
    """校验外键指向的班级 / 科目 / 老师存在且未删除，并给出可读的报错"""
    if class_id is not None:
        exists = db.query(Class.id).filter(Class.id == class_id, Class.is_deleted == 0).first()
        if not exists:
            raise ValueError(f"班级 {class_id} 不存在或已删除")
    if subject_id is not None:
        exists = db.query(Subject.id).filter(Subject.id == subject_id, Subject.is_deleted == 0).first()
        if not exists:
            raise ValueError(f"科目 {subject_id} 不存在或已删除")
    if teacher_id is not None:
        exists = db.query(Teacher.id).filter(Teacher.id == teacher_id, Teacher.is_deleted == 0).first()
        if not exists:
            raise ValueError(f"老师 {teacher_id} 不存在或已删除")


def _check_duplicate(db, class_id, subject_id, exclude_id=None):
    """同一个班同一科目只允许开一门课；如果要允许同班同科目多期，把这段校验去掉即可"""
    q = db.query(Course).filter(
        Course.class_id == class_id,
        Course.subject_id == subject_id,
        Course.is_deleted == 0,
    )
    if exclude_id is not None:
        q = q.filter(Course.id != exclude_id)
    if q.first():
        raise ValueError(f"班级 {class_id} 已经安排过科目 {subject_id} 的课程")


def _check_time(start_time, end_time):
    if start_time and end_time and end_time < start_time:
        raise ValueError("课程结束时间不能早于开始时间")

def _count_alive_scores(db, course_id):
    """统计该课程下还有多少条未删除的成绩"""
    return db.query(Score.id).filter(
        Score.course_id == course_id,
        Score.is_deleted == 0,
    ).count()


def create_course(db, data):
    _check_refs(db, data.class_id, data.subject_id, data.teacher_id)
    _check_duplicate(db, data.class_id, data.subject_id)
    _check_time(data.start_time, data.end_time)

    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db, course_id, data):
    course = _get_alive(db, course_id)
    if course is None:
        raise LookupError("课程不存在或已删除")

    values = data.model_dump(exclude_unset=True)
    _check_refs(db, values.get("class_id"), values.get("subject_id"), values.get("teacher_id"))

    # 只改了一个时间时，要拿库里的旧值和新的比
    new_class_id = values.get("class_id", course.class_id)
    new_subject_id = values.get("subject_id", course.subject_id)
    if "class_id" in values or "subject_id" in values:
        _check_duplicate(db, new_class_id, new_subject_id, exclude_id=course_id)
    _check_time(values.get("start_time", course.start_time), values.get("end_time", course.end_time))

    for field, value in values.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


def delete_course(db, course_id):
    """软删除：置 is_deleted=1，已录入的成绩记录仍然保留"""
    course = _get_alive(db, course_id)
    if course is None:
        raise LookupError("课程不存在或已删除")
    used = _count_alive_scores(db, course_id)
    if used:
        raise ValueError(f"课程 {course_id} 下还有 {used} 条成绩，请先删除成绩")

    course.is_deleted = 1
    db.commit()
    return True

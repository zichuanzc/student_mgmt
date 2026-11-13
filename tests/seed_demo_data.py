"""
导入演示用测试数据（体量适中，便于前端联调）
运行：在项目根目录执行  python tests/seed_demo_data.py
"""
import random
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import func

from app.core.database import Base, Session, engine
from app.models.class_ import Class
from app.models.class_teacher import class_teacher
from app.models.course import Course
from app.models.employment import Employment
from app.models.role import Role
from app.models.score import Score
from app.models.student import Student
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.user import User

Base.metadata.create_all(engine)
db = Session()


def table_count(model):
    return db.query(func.count(model.id)).scalar() or 0


def main():
    if table_count(Student) > 0:
        print("检测到已有学生数据，跳过重复导入。若需重来请先清空各表。")
        ensure_roles_and_admin()
        return
    _seed_all()


def ensure_roles_and_admin():
    if table_count(Role) < 3:
        for rid, name in [(2, "teacher"), (3, "student")]:
            if not db.query(Role).filter(Role.id == rid).first():
                db.add(Role(id=rid, name=name))
        db.commit()
    u = db.query(User).filter(User.role_id == 1, User.is_deleted == 0).first()
    if u and len(u.username) < 6:
        u.username = "admin001"
        db.commit()
    elif not db.query(User).filter(User.username == "admin001").first():
        db.add(
            User(
                username="admin001",
                password="123456",
                full_name="系统管理员",
                role_id=1,
                is_active=1,
                is_deleted=0,
            )
        )
        db.commit()
        print("已补充管理员账号 admin001 / 123456")


def _seed_all():

    if table_count(Role) == 0:
        roles = [
            {"id": 1, "name": "admin"},
            {"id": 2, "name": "teacher"},
            {"id": 3, "name": "student"},
        ]
        db.bulk_insert_mappings(Role, roles)
        db.commit()

    teachers = [
        {"teacher_code": 20001, "name": "王老师", "email": "wang@school.com", "is_head": 1},
        {"teacher_code": 20002, "name": "李老师", "email": "li@school.com", "is_head": 1},
        {"teacher_code": 20003, "name": "张老师", "email": "zhang@school.com", "is_head": 0},
        {"teacher_code": 20004, "name": "陈老师", "email": "chen@school.com", "is_head": 0},
        {"teacher_code": 20005, "name": "刘老师", "email": "liu@school.com", "is_head": 0},
    ]
    db.bulk_insert_mappings(Teacher, teachers)
    db.commit()
    teacher_rows = db.query(Teacher).order_by(Teacher.id).all()
    head_ids = [t.id for t in teacher_rows if t.is_head == 1]
    other_ids = [t.id for t in teacher_rows if t.is_head == 0]

    classes_data = [
        {
            "class_code": 20240101,
            "start_time": date(2024, 1, 8),
            "end_time": date(2024, 7, 8),
            "teacher_id": head_ids[0],
        },
        {
            "class_code": 20240201,
            "start_time": date(2024, 2, 1),
            "end_time": date(2024, 8, 1),
            "teacher_id": head_ids[1] if len(head_ids) > 1 else head_ids[0],
        },
        {
            "class_code": 20240301,
            "start_time": date(2024, 3, 1),
            "end_time": date(2024, 9, 1),
            "teacher_id": head_ids[0],
        },
    ]
    db.bulk_insert_mappings(Class, classes_data)
    db.commit()
    class_rows = db.query(Class).order_by(Class.id).all()

    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄"]
    givens = ["伟", "芳", "静", "强", "磊", "洋", "婷", "浩"]
    places = ["广东深圳", "湖南长沙", "湖北武汉", "四川成都", "江苏南京"]
    schools = ["武汉大学", "中山大学", "浙江大学", "华中科技大学"]
    majors = ["计算机科学与技术", "软件工程", "人工智能", "数据科学"]

    students_data = []
    for i in range(24):
        students_data.append(
            {
                "class_id": class_rows[i % len(class_rows)].id,
                "name": surnames[i % len(surnames)] + givens[(i + 1) % len(givens)],
                "native_place": places[i % len(places)],
                "graduate_school": schools[i % len(schools)],
                "major": majors[i % len(majors)],
                "enrollment_time": date(2020, 9, 1),
                "graduate_time": date(2024, 6, 30),
                "consultant_id": teacher_rows[i % len(teacher_rows)].id,
                "age": 20 + (i % 5),
                "gender": "男" if i % 2 == 0 else "女",
            }
        )
    db.bulk_insert_mappings(Student, students_data)
    db.commit()
    student_rows = db.query(Student).order_by(Student.id).all()

    subject_names = ["语文", "数学", "英语", "物理", "化学", "数据结构"]
    subjects_data = [{"subject_code": 1001 + i, "subject_name": n} for i, n in enumerate(subject_names)]
    db.bulk_insert_mappings(Subject, subjects_data)
    db.commit()
    subject_rows = db.query(Subject).order_by(Subject.id).all()

    course_data = []
    for c in class_rows:
        for j, sub in enumerate(subject_rows[:4]):
            course_data.append(
                {
                    "class_id": c.id,
                    "subject_id": sub.id,
                    "teacher_id": other_ids[j % len(other_ids)],
                    "start_time": c.start_time,
                    "end_time": c.end_time,
                }
            )
    db.bulk_insert_mappings(Course, course_data)
    db.commit()

    courses_by_class = defaultdict(list)
    for c in db.query(Course).all():
        courses_by_class[c.class_id].append(c.id)

    scores_data = []
    for i, s in enumerate(student_rows):
        for j, course_id in enumerate(courses_by_class.get(s.class_id, [])):
            scores_data.append(
                {
                    "stu_id": s.id,
                    "course_id": course_id,
                    "score": 58 + (i * 3 + j * 7) % 42,
                    "exam_order": 1,
                }
            )
    db.bulk_insert_mappings(Score, scores_data)
    db.commit()

    class_code_map = {c.id: c.class_code for c in class_rows}
    class_end_map = {c.id: c.end_time for c in class_rows}
    companies = ["腾讯科技", "阿里巴巴", "字节跳动", "华为", "美团"]

    employment_data = []
    for i, s in enumerate(student_rows):
        if i % 8 == 0:
            continue
        end = class_end_map[s.class_id]
        if not end:
            continue
        open_dt = datetime.combine(end + timedelta(days=10), time(9, 0))
        employment_data.append(
            {
                "student_id": s.id,
                "student_name": s.name,
                "class_code": class_code_map[s.class_id],
                "open_time": open_dt,
                "offer_time": open_dt + timedelta(days=20 + i % 15),
                "company": companies[i % len(companies)],
                "salary": Decimal(str(8000 + (i * 173) % 12000)),
            }
        )
    db.bulk_insert_mappings(Employment, employment_data)
    db.commit()

    allowed = defaultdict(set)
    for c in class_rows:
        if c.teacher_id:
            allowed[c.id].add(c.teacher_id)
    for course in db.query(Course).all():
        allowed[course.class_id].add(course.teacher_id)
    rows = [{"class_id": cid, "teacher_id": tid} for cid, tids in allowed.items() for tid in tids]
    if rows:
        db.execute(class_teacher.insert(), rows)
        db.commit()

    # 用户名至少 6 位（与用户接口校验一致）
    users = [
        {
            "username": "admin001",
            "password": "123456",
            "full_name": "系统管理员",
            "role_id": 1,
            "is_active": 1,
            "is_deleted": 0,
        },
        {
            "username": "teacher001",
            "password": "123456",
            "full_name": "王老师",
            "role_id": 2,
            "teacher_class_ids": "1,2",
            "is_active": 1,
            "is_deleted": 0,
        },
        {
            "username": "student001",
            "password": "123456",
            "full_name": student_rows[0].name,
            "role_id": 3,
            "is_active": 1,
            "is_deleted": 0,
        },
    ]
    db.bulk_insert_mappings(User, users)
    db.commit()

    print("演示数据导入完成：")
    print(f"  老师 {len(teacher_rows)}，班级 {len(class_rows)}，学生 {len(student_rows)}")
    print(f"  科目 {len(subject_rows)}，课程 {db.query(Course).count()}，成绩 {db.query(Score).count()}")
    print(f"  就业 {db.query(Employment).count()}，用户 {len(users)}")
    print("  管理员账号：admin001 / 123456（用户管理接口 query 参数 username=admin001）")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

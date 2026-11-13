# import sys
# from pathlib import Path
# # 把项目根（student_mgmt）加入 sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# print(sys.path)

import random

from app.core.database import  Base, engine,Session
from datetime import date, timedelta, datetime,time
from collections import defaultdict
from decimal import Decimal

from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.student import Student
from app.models.subject import Subject
from app.models.course import Course
from app.models.score import Score
from app.models.employment import Employment
from app.models.class_teacher import class_teacher
from app.models.role import Role
from app.models.user import User



# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
db = Session()
try:
    print("开始插入数据~~~")

    # # 测试数据：teacher
    # teachers_data = [{"teacher_code": f"2000{i}",
    #                   "name":f"teacher_{i+1}",
    #                   "email":f"teacher{18+i}@wl.com",
    #                   "is_head":f"{random.randint(0,1)}"
    #                   }
    #                  for i in range(100)]
    # db.bulk_insert_mappings(Teacher, teachers_data)
    # db.commit()


    # # 测试数据：class_
    # teacher_ids = [t.id for t in db.query(Teacher).filter(Teacher.is_head==1).all()]
    #
    # classes_data = [
    #     {
    #         "class_code": int(datetime.strftime(date(2024, 1, 1) + timedelta(days=7 * i), "%Y%m%d")),
    #         "start_time": date(2024, 1, 1) + timedelta(days=random.randint(7, 15) * i),
    #         "end_time": date(2024, 1, 1) + timedelta(days=random.randint(7, 60) * i + 150),
    #         "teacher_id": teacher_ids[i % len(teacher_ids)] if teacher_ids else None,
    #     }
    #     for i in range(100)
    # ]
    # db.bulk_insert_mappings(Class, classes_data)
    # db.commit()


    # # 测试数据：student
    # teacher_ids = [t.id for t in db.query(Teacher).all()]
    # class_ids = [c.id for c in db.query(Class).all()]
    #
    # surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    # givens = ["伟", "芳", "娜", "静", "丽", "强", "磊", "军", "洋", "勇", "好", "池", "浩", "祺", "武", "欢", "国"
    #           "汉", "黑子", "大壮", "小灰", "瑞", "芳", "恰", "卿", "霜", "爽儿", "心怡", "二狗", "狗蛋", "三儿", "大"]
    # places = ["广东深圳", "湖南长沙", "湖北武汉", "四川成都", "江苏南京",
    #           "浙江杭州", "山东济南", "河南郑州", "陕西西安", "福建厦门"]
    # schools = ["北京大学", "清华大学", "复旦大学", "浙江大学", "武汉大学",
    #            "中山大学", "四川大学", "南京大学", "华中科技大学", "西安交通大学"]
    # majors = ["计算机科学与技术", "软件工程", "电子信息工程", "通信工程", "自动化",
    #           "数学与应用数学", "统计学", "信息管理与信息系统", "网络工程", "人工智能"]
    #
    # students_data = [
    #     {
    #         "class_id": class_ids[i % len(class_ids)],
    #         "name": surnames[i % len(surnames)] + givens[i % len(surnames)] + givens[(i+random.randint(0,len(surnames))) % len(surnames)],
    #         "native_place": places[i % len(places)],
    #         "graduate_school": schools[i % len(schools)],
    #         "major": majors[i % len(majors)],
    #         "enrollment_time": date(2017, 9, 1) + timedelta(days=30 * (i % 12)),
    #         "graduate_time": date(2021, 7, 1) + timedelta(days=30 * (i % 12)),
    #         "consultant_id": teacher_ids[i % len(teacher_ids)] if teacher_ids else 1,
    #         "age": 18 + (i % 8),
    #         "gender": random.choice(["男", "女"]),
    #     }
    #     for i in range(1000)
    # ]
    # db.bulk_insert_mappings(Student, students_data)
    # db.commit()


    # # 测试数据：subject
    # subject_names = ["语文", "数学", "英语", "物理", "化学", "生物",
    #                  "历史", "地理", "政治", "体育", "音乐", "美术"]
    #
    # subjects_data = [
    #     {
    #         "subject_code": 1001 + i,
    #         "subject_name": name,
    #     }
    #     for i, name in enumerate(subject_names)
    # ]
    # db.bulk_insert_mappings(Subject, subjects_data)
    # db.commit()


    # # 测试数据：course
    # classes = db.query(Class).all()
    # subject_ids = [s.id for s in db.query(Subject).all()]
    # teacher_ids_all = [t.id for t in db.query(Teacher).filter(Teacher.is_head==0).all()]
    #
    # course_data = [
    #     {
    #         "class_id": c.id,
    #         "subject_id": subject_ids[j % len(subject_ids)],
    #         "teacher_id": teacher_ids_all[(idx * 5 + j) % len(teacher_ids_all)],
    #         "start_time": c.start_time + timedelta(days=30 * j),
    #         "end_time": c.end_time if j == 4 else c.start_time + timedelta(days=30 * j + 30),
    #     }
    #     for idx, c in enumerate(classes)
    #     for j in range(5)
    # ]
    # db.bulk_insert_mappings(Course, course_data)
    # db.commit()


    # # 测试数据：score
    # courses_by_class = defaultdict(list)
    # for c in db.query(Course).all():
    #     courses_by_class[c.class_id].append(c.id)
    #
    # students = db.query(Student).all()
    #
    # scores_data = [
    #     {
    #         "stu_id": s.id,
    #         "course_id": course_id,
    #         "score": random.randint(45, 100),
    #         "exam_order": 1,
    #     }
    #     for i, s in enumerate(students)
    #     for j, course_id in enumerate(courses_by_class.get(s.class_id, []))
    # ]
    # db.bulk_insert_mappings(Score, scores_data)
    # db.commit()


    # # 测试数据：employment
    # classes = db.query(Class).all()
    # students = db.query(Student).all()
    #
    # class_end_map = {c.id: c.end_time for c in classes}
    # class_code_map = {c.id: c.class_code for c in classes}
    #
    # companies = ["腾讯科技", "阿里巴巴", "字节跳动", "美团", "京东",
    #              "百度", "网易", "华为", "小米", "拼多多"]
    #
    # employment_data = [
    #     {
    #         "student_id": s.id,
    #         "student_name": s.name,
    #         "class_code": class_code_map[s.class_id],
    #         # 结课日 + 15~44 天，再拼上 9:00
    #         "open_time": datetime.combine(
    #             class_end_map[s.class_id] + timedelta(days=random.randint(0,7)),
    #             time(9, 0, 0),
    #         ),
    #         "offer_time": datetime.combine(
    #             class_end_map[s.class_id] + timedelta(days=random.randint(0,100)),
    #             time(9, 0, 0),
    #         ) + timedelta(days=14),
    #         "company": companies[i % len(companies)],
    #         "salary": Decimal(str(round(8000 + (i * 107) % 3900, 1))),
    #     }
    #     for i, s in enumerate(students)
    #     if i % 100 not in [0,1,2,3,4] and class_end_map[s.class_id] is not None  # 只给已结课的同学生成记录, 95%同学都顺利就业
    # ]
    # db.bulk_insert_mappings(Employment, employment_data)
    # db.commit()


    # # 测试数据：class_teacher
    # classes = db.query(Class).all()
    #
    # # 1. 构造每个班的白名单：班主任 + 该班授课老师
    # allowed = defaultdict(set)
    # for c in classes:
    #     if c.teacher_id:
    #         allowed[c.id].add(c.teacher_id)  # 班主任
    #
    # for course in db.query(Course).all():
    #     allowed[course.class_id].add(course.teacher_id)  # 授课老师
    #
    # # 2. 只遍历白名单，不碰其他老师
    # rows = list({
    #                 (c.id, t_id): {"class_id": c.id, "teacher_id": t_id}
    #                 for c in classes
    #                 for t_id in allowed[c.id]
    #             }.values())
    #
    # db.execute(class_teacher.insert(), rows)
    # db.commit()

    # # 测试数据：role
    # role_data = [
    #     {"id": 1, "name": "admin"},
    #     {"id": 2, "name": "teacher"},
    #     {"id": 3, "name": "student"}
    # ]
    # db.bulk_insert_mappings(Role, role_data)
    # db.commit()

    # # 测试数据：user
    # # password是用项目加密算法加密过的：明文对应：123456
    # user_data = [
    #     {"id": 1, "username": "admin", "password": "2d9d952832cd3b91e3d00bfc35533940", "full_name":"系统管理员", "role_id":1},
    #     {"id": 2, "username": "teacher001", "password": "2d9d952832cd3b91e3d00bfc35533940", "full_name": "第一位老师", "role_id":2},
    #     {"id": 3, "username": "student001", "password": "2d9d952832cd3b91e3d00bfc35533940", "full_name": "第一位学员", "role_id":3}
    # ]
    # db.bulk_insert_mappings(User, user_data)
    # db.commit()

    print("数据插入完成~~~")
except Exception as e:
    print(e)
    db.rollback()
finally:
    db.close()
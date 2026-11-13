"""负责数据库映射：student"""

from sqlalchemy import Column, Integer, String, DATE, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow



class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="学生编号")
    class_id = Column(Integer, ForeignKey("class_.id"),nullable=False, comment="学生班级")
    name = Column(String(25), nullable=False, comment="学生姓名")
    native_place = Column(String(50), nullable=False, comment="籍贯")
    graduate_school = Column(String(25), nullable=False, comment="毕业院校")
    major = Column(String(25), nullable=False, comment="专业")
    enrollment_time = Column(DATE, nullable=False, comment="入学时间")
    graduate_time = Column(DATE, nullable=False, comment="毕业时间")
    consultant_id = Column(Integer, ForeignKey("teacher.id"), nullable=False, comment="顾问编号")
    age = Column(Integer, nullable=False, comment="年龄")
    gender = Column(Enum("男", "女"), nullable=False, comment="性别")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")

    # 学生对应班级
    in_class = relationship("Class", back_populates="students")
    # 一个学生有多门课程成绩
    scores = relationship("Score", back_populates="student")
    # 获取学生最新的就业信息
    employment = relationship("Employment", back_populates="student")

    def __repr__(self):
        return f"<Student({self.__dict__})>"



# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

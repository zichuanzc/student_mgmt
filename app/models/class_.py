"""负责数据库映射：class_"""

from sqlalchemy import Column,Integer, ForeignKey, DATE, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.lib.tools import utcnow



class Class(Base):
    __tablename__ = "class_"
    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(Integer, nullable=False, comment="班级编号")
    start_time = Column(DATE, nullable=False, comment="开班时间")
    end_time = Column(DATE, nullable=True, default=None, comment="毕业时间")
    teacher_id = Column(Integer, ForeignKey("teacher.id"), comment="班主任")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")

    # 一个班级有多个学生
    students = relationship("Student", back_populates="in_class")
    # 一个班级对应一个班主任
    head_teacher = relationship("Teacher", back_populates="classes")
    # 一个班级会学习多门课程
    courses = relationship("Course", back_populates="in_class")
    # 一个班级有多个授课老师
    other_teachers = relationship("Teacher", secondary="class_teacher", back_populates="other_classes")

    def __repr__(self):
        return f"<Class({self.__dict__})>"



# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

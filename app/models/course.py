"""负责数据库映射：course"""

from sqlalchemy import Column, Integer, ForeignKey, DATE, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow



class Course(Base):
    __tablename__='course'
    id=Column(Integer,primary_key=True,autoincrement=True)
    class_id = Column(Integer, ForeignKey("class_.id"), nullable=False)
    subject_id =Column(Integer, ForeignKey("subject.id"), nullable=False)
    teacher_id =Column(Integer, ForeignKey("teacher.id"), nullable=False)
    start_time = Column(DATE, nullable=True, comment="课程开始时间")
    end_time = Column(DATE, default=None, comment="课程结束时间")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")


    # 课程对应的老师信息
    teacher = relationship("Teacher", back_populates="courses")
    # 一门课程对应多个学生成绩
    scores = relationship("Score", back_populates="course")
    # 该课程对应班级信息
    in_class = relationship("Class", back_populates="courses")


    def __repr__(self):
        return f"<Course({self.__dict__})>"

# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

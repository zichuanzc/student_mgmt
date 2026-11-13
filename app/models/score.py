"""负责数据库映射：score"""

from sqlalchemy import Column,Integer, ForeignKey,DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow



class Score(Base):
    __tablename__='score'
    id=Column(Integer,primary_key=True,nullable=False,autoincrement=True)
    stu_id=Column(Integer,ForeignKey('student.id'))
    course_id=Column(Integer,ForeignKey('course.id'))
    score=Column(Integer, nullable=False, comment="成绩")
    exam_order=Column(Integer, default=1, comment="考试批次")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")

    # 一个学生有多门课程成绩
    student = relationship("Student", back_populates="scores")
    # 一门课程对应多个学生成绩
    course = relationship("Course", back_populates="scores")


    def __repr__(self):
        return f"<Score({self.__dict__})>"

# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

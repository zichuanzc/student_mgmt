"""负责数据库映射：teacher"""

from sqlalchemy import Column,Integer,String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow




class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True, index=True)
    teacher_code = Column(Integer, unique=True, nullable=False, index=True, comment="教师编号")
    name = Column(String(25), index=True, nullable=False, comment="教师名称")
    email = Column(String(25), index=True, nullable=False, comment="教师邮箱")
    is_head = Column(Integer, nullable=False, comment="是否班主任（0不是，1是）")


    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")

    # 获取该老师是哪些班的班主任
    classes = relationship("Class", back_populates="head_teacher")
    # 一个老师可以上多门课程
    courses = relationship("Course", back_populates="teacher")
    # 一个老师可以给多个班级授课
    other_classes = relationship("Class", secondary="class_teacher", back_populates="other_teachers")



    def __repr__(self):
        return f"<Teacher({self.__dict__})>"



# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

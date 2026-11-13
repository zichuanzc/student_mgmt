"""负责数据库映射：employment"""

from sqlalchemy import Column,Integer,String,DateTime,DECIMAL,ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow



class Employment(Base):
    __tablename__ = "employment"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键自增id")
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False, comment="学生编号")
    student_name = Column(String(20), nullable=False, comment="学生姓名")
    class_code = Column(Integer, nullable=False, comment="学生班级")
    open_time = Column(DateTime, nullable=True, comment="就业开放时间")
    offer_time = Column(DateTime, nullable=True, comment="offer下发时间")
    company = Column(String(30), nullable=True, comment="就业公司名称")
    salary = Column(DECIMAL(7, 1), nullable=True, comment="就业薪资")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")

    # 根据关系获取对应学生信息
    student = relationship("Student",back_populates="employment")

    def __repr__(self):
        return f"<Employment({self.__dict__})>"

# # 创建所有表，建立映射
# Base.metadata.create_all(engine)




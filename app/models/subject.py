"""负责数据库映射：subject"""

from sqlalchemy import Column,Integer,String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base,engine
from app.lib.tools import utcnow

class Subject(Base):
    __tablename__='subject'
    id=Column(Integer,primary_key=True,autoincrement=True)
    subject_code = Column(Integer, unique=True, nullable=False, comment="科目编号")
    subject_name=Column(String(25),nullable=True, comment="科目名称")

    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")


    def __repr__(self):
        return f"<Subject({self.__dict__})>"

# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

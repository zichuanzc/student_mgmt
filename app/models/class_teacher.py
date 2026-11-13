"""负责数据库映射(中间表)：class_teacher"""

from sqlalchemy import Column,Integer,String, DateTime, Table, ForeignKey

from app.core.database import Base,engine




class_teacher = Table(
    "class_teacher",  # 中间表名
    Base.metadata,
    Column("class_id", Integer, ForeignKey("class_.id"), primary_key=True),
    Column("teacher_id", Integer, ForeignKey("teacher.id"), primary_key=True)
)



# # 创建所有表，建立映射
# Base.metadata.create_all(engine)

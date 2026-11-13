"""负责数据库映射：user"""

from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.lib.tools import utcnow



class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True,autoincrement=True,comment="用户id")#
    username = Column(String(50), unique=True, nullable=False,comment="用户名")
    password = Column(String(100), nullable=False,comment="用户密码")
    full_name = Column(String(50), nullable=True,comment="用户真实姓名")
    teacher_class_ids = Column(String(100), nullable=True,comment="用户是老师的时候，管理的班级id")
    role_id = Column(Integer, ForeignKey("role.id"), default=3,nullable=True,comment="外键约束，和role表的id关联")
    is_login = Column(Integer, default=0, nullable=False, comment="是否登录（0未登录，1已登录）")
    is_active = Column(Integer, default=1, nullable=False, comment="是否激活（0未激活，1激活）")
    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")#更新这条记录的时候，自动把update_time刷新为当前时间；新增时使用default赋值，修改时触发onupdate

    # 外键关联角色
    role = relationship("Role", back_populates="users")

    #User 和 Role 是**一对多关系**：一个角色 (Role) 可以对应多个用户 (User)，一个用户只能归属一个角色。
    #一对多的外键要放在**多的那一方**，也就是 User 表，增加`role_id`字段，存储角色的主键 id。如果把外键放到 Role 表，是做不到一对多存储多条用户 ID
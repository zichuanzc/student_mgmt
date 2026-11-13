"""负责数据库映射：role"""

from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.lib.tools import utcnow


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True,comment="角色id")
    name = Column(String(50), unique=True, nullable=False,comment="角色名")
    is_deleted = Column(Integer, default=0, nullable=False, comment="是否删除（0未删，1已删）")
    create_time = Column(DateTime, default=utcnow, comment="记录创建时间")
    update_time = Column(DateTime, default=utcnow, onupdate=utcnow, comment="记录更新时间")#更新这条记录的时候，自动把`update_time`刷新为当前时间；新增时使用`default`赋值，修改时触发`onupdate`

    # 反向：一个角色下有很多用户
    users = relationship("User", back_populates="role")




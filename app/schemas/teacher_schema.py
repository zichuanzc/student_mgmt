from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 1. 基础模型：包含老师通用的字段
class TeacherBase(BaseModel):
    teacher_code: Optional[int] = Field(None, description="教师编号")
    name: str = Field(..., min_length=2, max_length=25, description="教师名称")
    email: str = Field(..., max_length=25, description="教师邮箱")
    is_head: int = Field(..., description="是否班主任（0不是，1是）")

# 2. 新增老师专用：继承基础模型
class TeacherCreate(TeacherBase):
    pass

# 3. 修改老师
class TeacherUpdate(BaseModel):
    teacher_code: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    is_head: Optional[int] = None

# 4. 返回给前端
class TeacherOut(TeacherBase):
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型直接转为 Pydantic 模型
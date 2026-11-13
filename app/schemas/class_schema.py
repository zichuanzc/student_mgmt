from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

# 1. 基础模型：包含班级通用的字段
class ClassBase(BaseModel):
    class_code: int = Field(..., description="班级编号")
    start_time: date = Field(..., description="开班时间")
    end_time: Optional[date] = Field(None, description="毕业时间")
    teacher_id: int = Field(..., description="班主任ID")

# 2. 新增班级专用
class ClassCreate(ClassBase):
    pass

# 3. 修改班级专用：所有字段可选
class ClassUpdate(BaseModel):
    class_code: Optional[int] = None
    start_time: Optional[date] = None
    end_time: Optional[date] = None
    teacher_id: Optional[int] = None

# 4. 返回给前端专用
class ClassOut(ClassBase):
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True
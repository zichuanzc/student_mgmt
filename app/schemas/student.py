"""学生模块的请求体与响应体模型"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# 请求体模型
class StudentBase(BaseModel):
    """学生公共字段（与 models.Student 表字段一一对应）"""

    class_id: int = Field(..., description="所属班级ID")
    name: str = Field(..., max_length=25, description="学生姓名")
    native_place: str = Field(..., max_length=50, description="籍贯")
    graduate_school: str = Field(..., max_length=25, description="毕业院校")
    major: str = Field(..., max_length=25, description="专业")
    enrollment_time: date = Field(..., description="入学时间")
    graduate_time: date = Field(..., description="毕业时间")
    consultant_id: int = Field(..., description="顾问（教师）ID")
    age: int = Field(..., ge=0, le=100, description="年龄")
    gender: Literal["男", "女"] = Field(..., description="性别")

# 新增学生请求体：id 由数据库自增，前端无需传入
class StudentCreate(StudentBase):

    """更新学生请求体：全部字段可选，支持局部更新"""
class StudentUpdate(BaseModel):
    class_id: Optional[int] = Field(None, description="所属班级ID", json_schema_extra={"example": ""})
    name: Optional[str] = Field(None, max_length=25, description="学生姓名", json_schema_extra={"example": ""})
    native_place: Optional[str] = Field(None, max_length=50, description="籍贯", json_schema_extra={"example": ""})
    graduate_school: Optional[str] = Field(None, max_length=25, description="毕业院校", json_schema_extra={"example": ""})
    major: Optional[str] = Field(None, max_length=25, description="专业", json_schema_extra={"example": ""})
    enrollment_time: Optional[date] = Field(None, description="入学时间", json_schema_extra={"example": ""})
    graduate_time: Optional[date] = Field(None, description="毕业时间", json_schema_extra={"example": ""})
    consultant_id: Optional[int] = Field(None, description="顾问（教师）ID", json_schema_extra={"example": ""})
    age: Optional[int] = Field(None, ge=0, le=120, description="年龄", json_schema_extra={"example": ""})
    gender: Optional[Literal["男", "女"]] = Field(None, description="性别", json_schema_extra={"example": ""})

# 响应体模型
class StudentOut(StudentBase):
    """学生响应体：由 ORM 对象直接序列化"""
    id: int = Field(..., description="学生编号")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)  #从对象属性取值（from attributes），而不是只读取字典
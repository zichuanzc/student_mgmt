from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime
from typing import Optional

# 【1】超过年龄阈值的学生响应模型
class StudentOlderResponse(BaseModel):
    id: int
    class_id: int
    name: str
    native_place: Optional[str]
    graduate_school: Optional[str]
    major: Optional[str]
    enrollment_time: Optional[datetime]
    graduate_time: Optional[datetime]
    consultant_id: Optional[int]
    age: int
    gender: Optional[str]

    model_config = ConfigDict(from_attributes=True)




# 【2】班级性别统计响应模型
class ClassGenderStatResponse(BaseModel):
    class_id: int
    class_code: int
    total: int
    male_cnt: int
    female_cnt: int

    model_config = ConfigDict(from_attributes=True)
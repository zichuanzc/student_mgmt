

from pydantic import BaseModel, ConfigDict, Field, computed_field
from datetime import date, datetime,timedelta

from app.schemas.base import ApiResponse



# 定义请求体模型
class SalaryRankRequest(BaseModel):
    rank:int=Field(...)

class PerStudentTimeRequest(BaseModel):
    name: str | None = None

class PerClassTimeRequest(BaseModel):
    class_code: int | None = None



# 定义响应体模型
class SalaryRankResponse(BaseModel):
    """薪资前几名学员的就业信息"""
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象提取字段
    id:int
    student_id:int
    student_name:str
    class_code:int
    offer_time:datetime | None = None
    company: str
    salary:float


class SecondToDay(BaseModel):
    """秒转为天"""
    emp_seconds: int | None = Field(None, exclude=True)  # 秒数不对外展示
    @computed_field
    @property
    def emp_days(self) -> float | None:  # 将秒转换为天并添加到响应体中
        return round(self.emp_seconds / 86400, 1) if self.emp_seconds is not None else None

class TimePerStudentResponse(SecondToDay):
    """每个学员的就业时长"""
    id: int
    student_id: int
    student_name: str
    class_code: int
    offer_time: datetime | None = None

class TimePerClassResponse(TimePerStudentResponse):
    """每个班级的就业时长"""
    pass


class AvgTimePerClassResponse(SecondToDay):
    class_code:int






from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

# 新增就业信息，请求体效验模型
# 设计：新增接口只需要传学生编号，姓名、班级自动从学生表和班级表读取，减少前端工作量，保证冗余字段和主表一致
class EmploymentCreate(BaseModel):  # BaseModel 这是所有校验模型的基础类，EmploymentCreate 输入模型
    student_id: int = Field(...,description="需要结课并录入就业的学生编号")

# 修改就业信息的请求体模型
# 所有字段都是可选（默认 None），实现**部分更新**：前端只传要修改的字段即可，不用传完整数据，使用更灵活
class EmploymentUpdate(BaseModel):
    open_time: Optional[datetime] = None
    offer_time: Optional[datetime] = None
    company: Optional[str] = None
    salary: Optional[float] = None

# 就业信息的响应体模型
# 定义所有返回给前端的字段，和 ORM 模型字段名一一对应
class EmploymentOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    class_code: int
    open_time: Optional[datetime]
    offer_time: Optional[datetime]
    company: Optional[str]
    salary: Optional[float]

    # 支持直接把数据库的ORM对象转成响应模型
    model_config = ConfigDict(from_attributes=True)  # ConfigDict导包
    # model_config:类级别的模型配置入口
    # ConfigDict:配置容器
    # from_attributes=True：允许从对象属性读取数据，而非只从字典键读


# 列表分页返回：带总数，适配前端表格
class EmploymentListOut(BaseModel):
    total: int = Field(..., description="总记录数", ge=0)
    page: int = Field(..., description="当前页码", ge=1)
    page_size: int = Field(..., description="每页条数", ge=1)
    pages: int = Field(..., description="总页数", ge=0)
    items: List[EmploymentOut] = Field(..., description="当前页就业记录")


# # 薪资Top5响应
# class SalaryTop5Out(BaseModel):
#     student_name: str
#     class_code: str
#     offer_time: Optional[datetime]
#     company: Optional[str]
#     salary: float
#
#     model_config = ConfigDict(from_attributes=True)
#
# # 学生就业时长响应
# class StudentDurationOut(BaseModel):
#     student_id: int
#     student_name: str
#     class_code: str
#     employment_days: Optional[int]
#
#     model_config = ConfigDict(from_attributes=True)
#
# # 班级平均就业时长响应
# class ClassAvgDurationOut(BaseModel):
#     class_code: str
#     avg_duration_days: float
#
#     model_config = ConfigDict(from_attributes=True)











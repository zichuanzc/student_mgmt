# 负责请求体模型和响应体模型：course

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

# from schemas.common import Response


class CourseCreateRequest(BaseModel):
    """新增课程：一个班 + 一个科目 + 一个授课老师"""

    class_id: int = Field(..., ge=1, description="所属班级 id")
    subject_id: int = Field(..., ge=1, description="科目 id")
    teacher_id: int = Field(..., ge=1, description="授课老师 id")
    start_time: date | None = Field(default=None, description="课程开始时间")
    end_time: date | None = Field(default=None, description="课程结束时间")

    @model_validator(mode="after")
    def check_time(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("课程结束时间不能早于开始时间")
        return self


class CourseUpdateRequest(BaseModel):
    """修改课程：只传需要改的字段"""

    class_id: int | None = Field(default=None, ge=1, description="所属班级 id")
    subject_id: int | None = Field(default=None, ge=1, description="科目 id")
    teacher_id: int | None = Field(default=None, ge=1, description="授课老师 id")
    start_time: date | None = Field(default=None, description="课程开始时间")
    end_time: date | None = Field(default=None, description="课程结束时间")

    @model_validator(mode="after")
    def check_time(self):
        # 只校验同时传了两个时间的情况，只传一个时交给 dao 层结合库里的旧值再判断
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("课程结束时间不能早于开始时间")
        return self


class CourseOut(BaseModel):
    """课程输出结构，允许直接从 ORM 对象取值"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    class_id: int
    subject_id: int
    teacher_id: int
    start_time: date | None = None
    end_time: date | None = None


class CourseResponse(BaseModel):
    data: CourseOut | None = None


class CourseListResponse(BaseModel):
    total: int = 0
    data: list[CourseOut] = Field(default_factory=list)

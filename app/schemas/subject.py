# 负责请求体模型和响应体模型：subject

from pydantic import BaseModel, ConfigDict, Field

# from schemas.common import Response


class SubjectCreateRequest(BaseModel):
    """新增科目"""

    subject_code: int = Field(..., ge=1, description="科目编号（唯一）")
    subject_name: str | None = Field(default=None, max_length=25, description="科目名称")


class SubjectUpdateRequest(BaseModel):
    """修改科目：只传需要改的字段"""

    subject_code: int | None = Field(default=None, ge=1, description="科目编号（唯一）")
    subject_name: str | None = Field(default=None, max_length=25, description="科目名称")


class SubjectOut(BaseModel):
    """科目输出结构，允许直接从 ORM 对象取值"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_code: int
    subject_name: str | None = None


class SubjectResponse(BaseModel):
    data: SubjectOut | None = None


class SubjectListResponse(BaseModel):
    total: int = 0
    data: list[SubjectOut] = Field(default_factory=list)

# 负责请求体模型和响应体模型：score

from pydantic import BaseModel, ConfigDict, Field

# from schemas.common import Response


class ScoreCreateRequest(BaseModel):
    """新增成绩：学生 + 课程 + 考试批次 唯一"""

    stu_id: int = Field(..., ge=1, description="学生 id")
    course_id: int = Field(..., ge=1, description="课程 id")
    score: int | None = Field(default=None, ge=0, le=100, description="成绩（0-100）")
    exam_order: int | None = Field(default=None, ge=1, description="考试批次（第几次考试）")


class ScoreUpdateRequest(BaseModel):
    """按 score_id 修改成绩的请求体

    对应接口 PUT /score/{score_id} 已下线，改分统一走
    PUT /score/student/{stu_id}（ScoreByStudentUpdateRequest）。
    这个类先保留，方便以后恢复单条修改接口。
    """

    score: int | None = Field(default=None, ge=0, le=100, description="成绩（0-100）")
    exam_order: int | None = Field(default=None, ge=1, description="考试批次（第几次考试）")


class ScoreByStudentUpdateRequest(BaseModel):
    """按学生 + 课程定位一条成绩再改分数，不需要事先知道 score_id"""

    course_id: int = Field(..., ge=1, description="课程 id")
    exam_order: int | None = Field(default=None, ge=1, description="考试批次；不传则匹配未分批次的那条")
    score: int = Field(..., ge=0, le=100, description="修改后的成绩（0-100）")


class ScoreOut(BaseModel):
    """成绩输出结构，允许直接从 ORM 对象取值"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stu_id: int | None = None
    course_id: int | None = None
    score: int | None = None
    exam_order: int | None = None


class ScoreDetailOut(BaseModel):
    """成绩明细：联表带出学生姓名、科目名、老师名，供按学生/按老师查询使用"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stu_id: int | None = Field(default=None, description="学生 id")
    student_name: str | None = Field(default=None, description="学生姓名")
    class_code: int | None = Field(default=None, description="班级编号")
    course_id: int | None = Field(default=None, description="课程 id")
    subject_id: int | None = Field(default=None, description="科目 id")
    subject_name: str | None = Field(default=None, description="科目名称")
    teacher_id: int | None = Field(default=None, description="授课老师 id")
    teacher_name: str | None = Field(default=None, description="授课老师姓名")
    score: int | None = Field(default=None, description="成绩")
    exam_order: int | None = Field(default=None, description="考试批次")


class ScoreResponse(BaseModel):
    data: ScoreOut | None = None


class ScoreListResponse(BaseModel):
    total: int = 0
    data: list[ScoreOut] = Field(default_factory=list)


class ScoreDetailResponse(BaseModel):
    data: ScoreDetailOut | None = None


class ScoreDetailListResponse(BaseModel):
    total: int = 0
    data: list[ScoreDetailOut] = Field(default_factory=list)


class ScoreDeleteResponse(BaseModel):
    """批量删除的响应：告诉前端这次实际删了几条"""

    deleted: int = Field(default=0, description="本次软删除的成绩条数")


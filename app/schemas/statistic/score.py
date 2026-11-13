from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# 1. 所有成绩都达标的学生响应（带成绩数组）
class StudentAllScorePassResponse(BaseModel):
    stu_id: int
    name: str
    scores: List[int]

    model_config = ConfigDict(from_attributes=True)

    #所有成绩都达标的学生响应（不带成绩数组）
class StudentPassPassResponse(BaseModel):
    stu_id: int
    name: str
    score: int

    model_config = ConfigDict(from_attributes=True)

# 2. 不及格次数达标学生响应（带不及格成绩数组）
class StudentFailManyResponse(BaseModel):
    name: str
    class_code: int
    fail_scores: List[int]
    model_config = ConfigDict(from_attributes=True)

    # 不及格次数达标学生响应（不带不及格成绩数组）
class StudentFailScoreResponse(BaseModel):
    stu_id: int
    name: str
    class_code: int
    score: int

    model_config = ConfigDict(from_attributes=True)

# 3. 班级每场考试平均分
class ClassExamAvgScoreResponse(BaseModel):
    class_id: int
    class_code: int
    exam_order: int | None = None
    avg_score: float

    model_config = ConfigDict(from_attributes=True)
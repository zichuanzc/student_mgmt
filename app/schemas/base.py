"""请求响应基类，定义请求体响应头规范"""

from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

# 定义泛型
T = TypeVar("T")


# 响应体，普通响应体
class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None

# 响应体，分页响应体
class PageResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    data: List[T]

# 响应头，总数响应体
class TotalResponse(BaseModel, Generic[T]):
    total: int
    data: List[T]

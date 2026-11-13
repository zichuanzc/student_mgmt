import hashlib
from datetime import datetime, timezone
from app.core.config import SALT

def utcnow():
    """获取当前时间"""
    return datetime.now(timezone.utc)

def get_specified_page(rows, page=1, size=10):
    """获取传入序列中指定页中对应数据，默认返回第一页，每页10条数据"""
    total = len(rows)
    if total <= size:  # 第一页
        return total, rows
    elif total < page * size:  # 最后一页，页码范围不合理时，默认返回最后一页
        return total, rows[-(total % size):]
    else:  # 其他页
        return total, rows[(page - 1) * size: page * size]


def md5_hash(plain: str, salt: str = SALT, upper: bool = False) -> str:
    """MD5 加密（哈希）。
    plain: 明文
    salt:  盐，默认为项目盐
    upper: 是否返回大写
    """
    if not isinstance(plain, str):
        raise TypeError("plain 必须是 str")
    data = salt
    for c in plain:
        data += c+salt
    data = data.encode("utf-8")
    digest = hashlib.md5(data).hexdigest()
    return digest.upper() if upper else digest
# print(md5_hash("123456"))



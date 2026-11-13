from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from app.core.config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建模型基类
Base = declarative_base()

# 创建会话
Session = sessionmaker(bind=engine)


# 每个接口都要用到会话，会话用完要立即关闭
# 需要用到时才给，不需要不给，所以应该把它做成生成器
def get_db():
    try:
        db=Session()
        yield db
    finally:
        db.close()
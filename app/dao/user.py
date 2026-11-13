from sqlalchemy.orm import Session
from app.models.user import User



#根据用户名查询未被软删除的用户
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username, User.is_deleted == 0).first()
#根据id查询所有用户，包含被软删除的用户
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

#查询所有未被软删除的用户
def get_all_user(db: Session):
    return db.query(User).filter(User.is_deleted == 0).all()


#统计user表中管理员的总数，因为只能有一个管理员，且该管理员是不能被删除的，所以没有必要加上User.is_deleted==0这个条件
def count_admin(db: Session):
    return db.query(User).filter(User.role_id == 1).count()
#新增用户，提交到数据库并刷新数据库
def create_user(db: Session, user_obj: User):
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

#修改用户，更新这个用户
def commit_and_refresh_user(db: Session,user_obj:User):
    db.commit()
    db.refresh(user_obj)
#只软删除用户
def soft_delete_user(db: Session, user_obj: User):
    user_obj.is_deleted = 1
    db.commit()
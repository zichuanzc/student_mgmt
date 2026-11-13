# 负责操作数据库，增删改查：subject

from app.models.subject import Subject


def _get_alive(db, subject_id):
    """取出未删除的科目，删掉的一律当作不存在"""
    return db.query(Subject).filter(Subject.id == subject_id, Subject.is_deleted == 0).first()


def get_subject(db, subject_id):
    return _get_alive(db, subject_id)


def list_subjects(db, page, size, keyword=None):
    q = db.query(Subject).filter(Subject.is_deleted == 0)
    if keyword:
        q = q.filter(Subject.subject_name.like(f"%{keyword}%"))
    total = q.count()
    rows = q.order_by(Subject.id).offset((page - 1) * size).limit(size).all()
    return rows, total


def _check_code_unique(db, subject_code, exclude_id=None):
    q = db.query(Subject).filter(Subject.subject_code == subject_code, Subject.is_deleted == 0)
    if exclude_id is not None:
        q = q.filter(Subject.id != exclude_id)
    if q.first():
        raise ValueError(f"科目编号 {subject_code} 已存在")


def create_subject(db, data):
    _check_code_unique(db, data.subject_code)
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update_subject(db, subject_id, data):
    subject = _get_alive(db, subject_id)
    if subject is None:
        raise LookupError("科目不存在或已删除")

    values = data.model_dump(exclude_unset=True)  # 只拿请求里真正传了的字段
    if "subject_code" in values:
        _check_code_unique(db, values["subject_code"], exclude_id=subject_id)
    for field, value in values.items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db, subject_id):
    """软删除：置 is_deleted=1，保留历史课程对它的引用"""
    subject = _get_alive(db, subject_id)
    if subject is None:
        raise LookupError("科目不存在或已删除")

    subject.is_deleted = 1
    db.commit()
    return True

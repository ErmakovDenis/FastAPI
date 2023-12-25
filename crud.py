from sqlalchemy.orm import Session

import schemas
from models import User, Item


# Category
def create_user(db: Session, schema: schemas.UserCreate):
    db_category = User(**schema.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter_by(id=user_id).first()


def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate | dict):
    db_user = db.query(User).filter_by(id=user_id).first()

    user_data = user_data if isinstance(user_data, dict) else user_data.model_dump()

    if db_user:
        for k, v in user_data.items():
            if hasattr(db_user, k):
                setattr(db_user, k, v)

        db.commit()
        db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter_by(id=user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Item
def create_item(db: Session, schema: schemas.ItemCreate):
    db_item = Item(**schema.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int):
    return db.query(Item).filter_by(id=item_id).first()


def update_item(db: Session, item_id: int, item_data: schemas.ItemUpdate | dict):
    db_item = db.query(Item).filter_by(id=item_id).first()

    item_data = item_data if isinstance(item_data, dict) else item_data.model_dump()

    if db_item:
        for key, value in item_data.items():
            if hasattr(db_item, key):
                setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
        return db_item
    return None


def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter_by(id=item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

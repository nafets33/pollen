from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from . import models, schemas
from helpers.auth import get_password_hash
from exceptions.user import user_already_exists_exception

class User:

    @staticmethod
    def get_user_by_id(id: int, db: Session):
        return db.query(models.User).filter(models.User.id == id).first()

    @staticmethod
    def get_user_by_email(email: str, db: Session):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create_user(user: schemas.UserBase, db: Session):
        try:
            user.password = get_password_hash(user.password)
            db_user = models.User(**user.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            raise user_already_exists_exception

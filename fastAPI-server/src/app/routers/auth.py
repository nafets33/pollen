from fastapi import APIRouter, status, Body, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from helpers.auth import create_access_token, verify_password
from database.schemas import UserSchema, UserBase, Token
from database.queries import User
from database.db import get_db
from middleware.auth import is_autheticated

from exceptions.user import user_not_found_exception, incorrect_password_exception, user_already_exists_exception

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
def login(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    user = User.get_user_by_email(email, db)
    if not user:
        raise user_not_found_exception
    if not verify_password(password, user.password):
        raise incorrect_password_exception
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={
            "id": user.id,
            "email" : user.email
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=f"Bearer {access_token}")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
def register(body: UserBase, db: Session = Depends(get_db)):
    user = User.create_user(body, db)
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={
            "id": user.id,
            "email" : user.email
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=f"Bearer {access_token}")

@router.get("/user", status_code=status.HTTP_200_OK, response_model=UserSchema)
def get_user(user_id: int = Depends(is_autheticated), db: Session = Depends(get_db)):
    user = User.get_user_by_id(user_id,db)
    print(user)
    if not user:
        raise user_not_found_exception
    return user

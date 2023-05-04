from fastapi import HTTPException, status, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database.db import get_db
import os

from exceptions.user import token_exception

async def is_autheticated(authorization: str = Header(...), db: Session = Depends(get_db)):
    token: str = authorization.split()[-1]
    try:
        payload = jwt.decode(
            token,
            os.environ.get("SECRET_KEY"),
            algorithms=os.environ.get("ALGORITHM")
        )
        return payload.get("id")
    except JWTError:
        raise token_exception

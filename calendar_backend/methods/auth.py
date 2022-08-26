from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from calendar_backend.settings import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str


class UserInDB(User):
    password: str


def get_user(db, username: str):
    if username in db:
        password = db[username]
        return UserInDB(username=username, password=password)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(settings.ADMIN_SECRET, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user.username

import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from calendar_backend import get_settings
from calendar_backend.methods import auth

auth_router = APIRouter(prefix="", tags=["Auth"])
settings = get_settings()
logger = logging.getLogger(__name__)


@auth_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = settings.ADMIN_SECRET.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = auth.UserInDB(**user_dict)
    hashed_password = form_data.password
    if not hashed_password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


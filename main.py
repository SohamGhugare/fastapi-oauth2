from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, Oauth2PasswordRequestForm
from passlib.context import CryptContext

import uvicorn

from models import UserModel
from database import Database

app = FastAPI()
db = Database()
# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Oauth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing and verifying
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_hash(raw_password: str, hashed_password: str):
    return pwd_context.verify(raw_password, hashed_password)

# Util funcs
# TODO: Move to separate file
def get_current_active_user():
    pass

@app.get("/")
async def index():
    return "Hello World"

@app.post("/token")
async def login(form_data: Oauth2PasswordRequestForm = Depends()):
    user = db.get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password.")
    hashed_password = get_password_hash(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password.")

    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)

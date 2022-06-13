from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

import uvicorn

from models import UserModel
from database import Database
from sqlmodel import SQLModel

# VARIABLES
SECRET_KEY = "674b53543cd8db0a298e4d973db04d733ebcc5a22cce4d8ae900ef4492f904c3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Utility classes
class UserIn(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None

# Util funcs
# TODO: Move to separate file

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.get_user(username=token_data.username)
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def authenticate_user(username: str, password: str):
    user = db.get_user(username)
    if not user:
        return False
    if not verify_hash(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None=None ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def index():
    return "Hello World"

@app.post("/token", response_model = Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user

@app.post("/create-user")
def create_new_user(user: UserIn):
    user_model = UserModel(
        username = user.username,
        hashed_password = get_password_hash(user.password)
    )
    db.create_user(user_model)
    return {"Response": "User created successfully"}

if __name__ == '__main__':
    
    uvicorn.run("main:app", reload=True)

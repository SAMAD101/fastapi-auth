from fastapi import FastAPI, Request, Response, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pathlib import Path
from typing import Annotated
from sqlmodel import Session
from datetime import timedelta

from .database import create_db_and_tables, SessionDep
from .models import User
from .schemas import Token, User as UserSchema
from .utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    SECRET_KEY,
)


app: FastAPI = FastAPI(title="fastapi-auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR: Path = Path(__file__).resolve().parent

templates: Jinja2Templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionDep)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(SessionDep),
) -> Response:
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            detail="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"{access_token}", httponly=True)
    return response


@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request) -> Response:
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> Response:
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    role: str = "user",
    db: Session = Depends(SessionDep),
) -> Response:
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
    )
    if db.get(User, username):
        raise HTTPException(
            detail="User with this username already exists",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            detail="User with this email already exists",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login")


@app.get("/protected")
async def protected_route(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(SessionDep),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return {"message": "Welcome to protected route", "user": user.username}

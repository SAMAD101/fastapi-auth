from fastapi import FastAPI, Request, Response, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from pathlib import Path
from typing import Annotated
from sqlmodel import Session
from datetime import timedelta

from .database import create_db_and_tables, get_db
from .models import User
from .utils import (
    get_password_hash,
    create_access_token,
    authenticate_user,
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


@app.get("/protected", response_class=HTMLResponse)
async def protected(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request.cookies.get("access_token"), db)
    print(user)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
) -> Response:
    user = await authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            detail="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    response = RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"{access_token}", httponly=True)
    return response


@app.get("/logout", response_class=RedirectResponse, dependencies=[])
async def logout(request: Request) -> Response:
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
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
    db: Session = Depends(get_db),
) -> Response:
    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"There was an error registering the user: {e}",
        )
    return RedirectResponse(url="/login")

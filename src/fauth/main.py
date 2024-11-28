from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from pathlib import Path

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


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> Response:
    return templates.TemplateResponse("register.html", {"request": request})

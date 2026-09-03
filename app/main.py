from app.routers import clients
from app.routers import auth
from app.routers import beverages
from app.routers import orders
from datetime import date
from sqlalchemy.orm import Session
from app.database import models
from app.dependencies import get_db, create_tables
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

create_tables()

app = FastAPI(title="Spirits Distribution Portal")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.add_middleware(SessionMiddleware, secret_key="ssVWrQ[1TfjIaE;{")

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(beverages.router)
app.include_router(orders.router)

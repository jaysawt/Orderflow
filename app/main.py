from app.routers import clients
import math
from datetime import date
from sqlalchemy.orm import Session
from app.routers import auth
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
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(auth.router)
app.include_router(clients.router)

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    session_id = request.session.get("user_id")
    if not session_id:
        return RedirectResponse(url="/login")

    user = db.query(models.User).filter(models.User.id == session_id).first()
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "orders": []
        }
    )

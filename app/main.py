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

@app.get('/clients', response_class=HTMLResponse)
def clients_page(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    client_saved: bool = False,
    client_deleted: bool = False,
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    session_id = request.session.get("user_id")
    if not session_id:
        return RedirectResponse(url="/login")

    client_saved_msg = "Client saved successfully" if client_saved else ""
    client_deleted_msg = "Client deleted successfully" if client_deleted else ""

    user = db.query(models.User).filter(models.User.id == session_id).first()
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    # Normalize filter parameters
    status_val = status if status in ("0", "1") else None
    search_val = search.strip() if search and search.strip() else None

    # Dynamic query with combined filters
    query = db.query(models.Client)
    if status_val is not None:
        query = query.filter(models.Client.status == int(status_val))
    if search_val:
        search_term = f"%{search_val}%"
        query = query.filter(
            models.Client.outlet_name.ilike(search_term) | 
            models.Client.location.ilike(search_term)
        )

    page_size = 5
    total_clients = query.count()
    total_pages = max(1, math.ceil(total_clients / page_size)) if total_clients > 0 else 1

    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1

    offset = (page - 1) * page_size
    clients = query.order_by(models.Client.id.asc()).offset(offset).limit(page_size).all()

    start_index = (page - 1) * page_size + 1 if total_clients > 0 else 0
    end_index = min(page * page_size, total_clients)

    return templates.TemplateResponse(
        request=request,
        name="clients.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "client_saved": client_saved_msg,
            "client_deleted": client_deleted_msg,
            "active_tab": "Clients",
            "clients": clients,
            "page": page,
            "total_pages": total_pages,
            "total_clients": total_clients,
            "start_index": start_index,
            "end_index": end_index,
            "page_size": page_size,
            "status": status_val,
            "search": search_val or ""
        }
    )

@app.get('/add-edit-client', response_class=HTMLResponse)
def add_edit_client_page(request: Request, db: Session = Depends(get_db), client_id: Optional[int] = Query(None)):
    session_id = request.session.get("user_id")
    if not session_id:
        return RedirectResponse(url="/login")

    user = db.query(models.User).filter(models.User.id == session_id).first()
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()
    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
    else:
        client = None

    return templates.TemplateResponse(
        request=request,
        name="add_edit_client.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "active_tab": "Clients",
            "client": client,
        }
    )

@app.post('/add-edit-client', response_class=HTMLResponse)
def add_edit_client(request:Request, client_id: Optional[int] = Form(None), outlet_name: str = Form(...), location: str = Form(...), status: int = Form(...),db: Session = Depends(get_db)):
    session_id = request.session.get("user_id")
    if not session_id:
        return RedirectResponse(url="/login")

    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        client.outlet_name = outlet_name
        client.location = location
        client.status = status
        db.commit()
    else:
        new_client = models.Client(outlet_name = outlet_name, location = location, status=status)
        db.add(new_client)
        db.commit()
    
    return RedirectResponse(url="/clients?client_saved=True", status_code=303)

@app.get('/delete-client', response_class=HTMLResponse)
def delete_client(request: Request, client_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    session_id = request.session.get("user_id")
    if not session_id:
        return RedirectResponse(url="/login")

    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if client:
            db.delete(client)
            db.commit()

    return RedirectResponse(url="/clients?client_deleted=True", status_code=303)
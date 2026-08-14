import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, templates
from app.database import models
from app.validation import ClientForm
from pydantic import ValidationError

router = APIRouter()

@router.get('/clients', response_class=HTMLResponse)
def clients_page(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    client_saved: bool = False,
    client_deleted: bool = False,
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user: models.User = Depends(get_current_user)
):

    client_saved_msg = "Client saved successfully" if client_saved else ""
    client_deleted_msg = "Client deleted successfully" if client_deleted else ""

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

@router.get('/add-edit-client', response_class=HTMLResponse)
def add_edit_client_page(request: Request, db: Session = Depends(get_db), client_id: Optional[int] = Query(None), user: models.User = Depends(get_current_user)):

    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()
    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            return RedirectResponse(url="/clients?client_saved=False", status_code=303)
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

@router.post('/add-edit-client', response_class=HTMLResponse)
def add_edit_client(
    request: Request,
    client_id: Optional[int] = Form(None),
    outlet_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):

    try:
        data = ClientForm(outlet_name=outlet_name, location=location, status=status)
    except ValidationError as e:
        username = user.username if user else "Admin"
        current_date_str = date.today().isoformat()
        return templates.TemplateResponse(
            request=request,
            name="add_edit_client.html",
            context={
                "username": username,
                "current_date": current_date_str,
                "active_tab": "Clients",
                "client": {
                    "id": client_id,
                    "outlet_name": outlet_name or "",
                    "location": location or "",
                    "status": status if status is not None else 1
                },
                "error": "Field cannot be empty"
            }
        )

    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if not client:
            return RedirectResponse(url="/clients?client_saved=False", status_code=303)
        client.outlet_name = data.outlet_name
        client.location = data.location
        client.status = data.status
        db.commit()
    else:
        new_client = models.Client(outlet_name=data.outlet_name, location=data.location, status=data.status)
        db.add(new_client)
        db.commit()
    
    return RedirectResponse(url="/clients?client_saved=True", status_code=303)

@router.post('/delete-client', response_class=HTMLResponse)
def delete_client(client_id: Optional[int] = Query(None), db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if client_id:
        client = db.query(models.Client).filter(models.Client.id == client_id).first()
        if client:
            db.delete(client)
            db.commit()

    return RedirectResponse(url="/clients?client_deleted=True", status_code=303)
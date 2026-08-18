import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, templates
from app.database import models

router = APIRouter()

@router.get('/orders', response_class=HTMLResponse)
def orders_page(request: Request, user: models.User = Depends(get_current_user)):

    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "active_tab": "Orders",
            "orders": []
        }
    )

@router.get('/add-edit-order', response_class=HTMLResponse)
def add_edit_order_page(
    request: Request,
    db: Session = Depends(get_db),
    order_id: Optional[int] = Query(None),
    user: models.User = Depends(get_current_user)
):
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    clients = db.query(models.Client).filter(models.Client.status == 1).order_by(models.Client.outlet_name.asc()).all()
    beverages = db.query(models.Beverage).order_by(models.Beverage.product_brand.asc()).all()

    return templates.TemplateResponse(
        request=request,
        name="add_edit_order.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "active_tab": "Orders",
            "clients": clients,
            "beverages": beverages,
            "order": None,
            "error": None
        }
    )

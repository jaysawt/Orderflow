import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, templates
from app.database import models
from app.validation import BeverageForm
from pydantic import ValidationError

router = APIRouter()

@router.get('/beverages', response_class=HTMLResponse)
def beverage_client(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    beverage_saved: bool = False,
    beverage_deleted: bool = False,
    search: Optional[str] = Query(None),
    user: models.User = Depends(get_current_user)
):
    beverage_saved_msg = "Beverage saved successfully" if beverage_saved else ""
    beverage_deleted_msg = "Beverage deleted successfully" if beverage_deleted else ""
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    search_val = search.strip() if search and search.strip() else None

    query = db.query(models.Beverage)

    if search_val:
        search_term = f"%{search_val}%"
        query = query.filter(
            models.Beverage.product_brand.ilike(search_term)
        )
    
    page_size = 5
    total_beverages = query.count()
    total_pages = max(1, math.ceil(total_beverages / page_size)) if total_beverages > 0 else 1

    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1

    offset = (page - 1) * page_size
    beverages = query.order_by(models.Beverage.id.asc()).offset(offset).limit(page_size).all()

    start_index = (page - 1) * page_size + 1 if total_beverages > 0 else 0
    end_index = min(page * page_size, total_beverages)

    return templates.TemplateResponse(
        request=request,
        name="beverages.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "beverage_saved": beverage_saved_msg,
            "beverage_deleted": beverage_deleted_msg,
            "active_tab": "Beverages",
            "beverages": beverages,
            "page": page,
            "total_pages": total_pages,
            "total_beverages": total_beverages,
            "start_index": start_index,
            "end_index": end_index,
            "page_size": page_size,
            "search": search_val or ""
        }
    )


@router.get('/add-edit-beverage', response_class=HTMLResponse)
def add_edit_beverage_page(request: Request, db: Session = Depends(get_db), beverage_id: Optional[int] = Query(None), user: models.User = Depends(get_current_user)):
    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    if beverage_id:
        beverage = db.query(models.Beverage).filter(models.Beverage.id == beverage_id).first()
        if not beverage:
            return RedirectResponse(url="/beverages?error=Beverage+not+found", status_code=303)
    else:
        beverage = None

    return templates.TemplateResponse(
        request=request,
        name="add_edit_beverage.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "active_tab": "Beverages",
            "beverage": beverage,
            "beverage_id": beverage_id
        }
    )

@router.post('/add-edit-beverage', response_class=HTMLResponse)
def add_edit_beverage(
    request: Request,
    db: Session = Depends(get_db),
    beverage_id: Optional[int] = Form(None),
    product_brand: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    user: models.User = Depends(get_current_user)
):
    try:
        data = BeverageForm(product_brand=product_brand, quantity=quantity, price=price)
    except ValidationError as e:
        username = user.username if user else "Admin"
        current_date_str = date.today().isoformat()
        return templates.TemplateResponse(
            request=request,
            name="add_edit_beverage.html",
            context={
                "username": username,
                "current_date": current_date_str,
                "active_tab": "Beverages",
                "beverage": {
                    "id": beverage_id,
                    "product_brand": product_brand or "",
                    "quantity": quantity or "",
                    "price": price or ""
                },
                "error": f"{e.errors()[0]['msg']}"
            }
        )
    
    if beverage_id:
        beverage = db.query(models.Beverage).filter(models.Beverage.id == beverage_id).first()
        if not beverage:
            return RedirectResponse(url="/beverages?beverage_saved=False", status_code=303)
        beverage.product_brand = data.product_brand
        beverage.quantity = data.quantity
        beverage.price = data.price
        db.commit()
    else:
        new_beverage = models.Beverage(product_brand=data.product_brand, quantity=data.quantity, price=data.price)
        db.add(new_beverage)
        db.commit()
    
    return RedirectResponse(url="/beverages?beverage_saved=True", status_code=303)

@router.post('/delete-beverage', response_class=HTMLResponse)
def delete_beverage(beverage_id: Optional[int] = Form(None), db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if beverage_id:
        beverage = db.query(models.Beverage).filter(models.Beverage.id == beverage_id).first()
        if beverage:
            db.delete(beverage)
            db.commit()
    
    return RedirectResponse(url="/beverages?beverage_deleted=True", status_code=303)

    

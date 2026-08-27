import math
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, templates
from app.database import models
from app.validation import OrderForm, OrderItemForm
from pydantic import ValidationError

def generate_order_name(db: Session) -> str:
    """Generates a unique order name in the format ORD-YYYYMMDD-XXX"""
    today = date.today().strftime("%Y%m%d")
    count_today = db.query(models.Order).filter(models.Order.order_name.like(f"ORD-{today}-%")).count()
    return f"ORD-{today}-{count_today + 1:03d}"

router = APIRouter()

@router.get('/orders', response_class=HTMLResponse)
def orders_page(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    order_saved: bool = False,
    order_delete: bool = False,
    order_edit: bool = False,
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):

    username = user.username if user else "Admin"
    current_date_str = date.today().isoformat()

    order_saved_msg = "Order saved successfully" if order_saved else ""
    order_delete_msg = "Order deleted successfully" if order_delete else ""
    order_edit_msg = "Order updated successfully" if order_edit else ""

    # Normalize filter parameters
    status_val = status if status in ("0", "1") else None
    search_val = search.strip() if search and search.strip() else None

    query = db.query(models.Order).join(models.Client)
    if status_val is not None:
        query = query.filter(models.Order.status == int(status_val))
    if search_val:
        search_term = f"%{search_val}%"
        query = query.filter(
            models.Order.order_name.ilike(search_term) | 
            models.Client.outlet_name.ilike(search_term)
        )
    
    #pagination
    page_size = 10
    total_orders = query.count()
    total_pages = max(1, math.ceil(total_orders / page_size)) if total_orders > 0 else 1
    
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    
    offset = (page - 1) * page_size
    orders = query.order_by(models.Order.id.desc()).offset(offset).limit(page_size).all()
    
    start_index = (page - 1) * page_size + 1 if total_orders > 0 else 0
    end_index = min(page * page_size, total_orders)

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "username": username,
            "current_date": current_date_str,
            "active_tab": "Orders",
            "order_saved": order_saved_msg,
            "order_delete": order_delete_msg,
            "order_edit": order_edit_msg,
            "orders": orders,
            "page": page,
            "total_pages": total_pages,
            "total_orders": total_orders,
            "start_index": start_index,
            "end_index": end_index,
            "page_size": page_size,
            "status": status_val,
            "search": search_val or ""
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

    if order_id:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            return RedirectResponse(url="/orders?order_saved=False", status_code=303)
    else:
        order = None

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
            "order": order
        }
    )

@router.post('/add-edit-order', response_class=HTMLResponse)
def add_edit_order(
    request: Request, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user),
    order_id: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    beverage_id: List[str] = Form([], alias="beverage_id[]"),
    price: List[str] = Form([], alias="price[]"),
    quantity: List[str] = Form([], alias="quantity[]"),
    cases: List[str] = Form([], alias="cases[]"),
    discount: List[str] = Form([], alias="discount[]"),
    total_price: List[str] = Form([], alias="total_price[]"),
    grand_total: Optional[str] = Form(None)
):
    try:
        order_summary = OrderForm(client_id=client_id, status=status, grand_total=grand_total)
        order_data = []
        for i in range(len(beverage_id)):
            item = OrderItemForm(beverage_id=beverage_id[i], mrp=price[i], quantity=quantity[i], cases=cases[i], discount=discount[i], total_price=total_price[i])
            order_data.append(item)
    except ValidationError as e:
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
                "order": {
                    "client_id": client_id,
                    "status": status,
                    "grand_total": grand_total,
                },
                "error": e.errors()
            }
        )
    
    if order_id:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            return RedirectResponse(url="/orders?order_saved=False", status_code=303)
        order.status = order_summary.status
        order.grand_total = order_summary.grand_total
        db.commit()

        order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
        incoming_data_map = {item.beverage_id: item for item in order_data}
        for item in order_items:
            if item.beverage_id in incoming_data_map:
                new_data = incoming_data_map[item.beverage_id]
                item.mrp = new_data.mrp
                item.quantity = new_data.quantity
                item.cases = new_data.cases
                item.discount = new_data.discount
                item.total_price = new_data.total_price
                del incoming_data_map[item.beverage_id]
            else:
                db.delete(item)
        
        for beverage_id, new_data in incoming_data_map.items():
            new_item = models.OrderItem(
                order_id=order_id,
                beverage_id=beverage_id,
                mrp=new_data.mrp,
                quantity=new_data.quantity,
                cases=new_data.cases,
                discount=new_data.discount,
                total_price=new_data.total_price
            )
            db.add(new_item)
        db.commit()
        return RedirectResponse(url='/orders?order_edit=True', status_code=303)
    else:
        order = models.Order(order_name=generate_order_name(db), client_id=order_summary.client_id, status=order_summary.status, grand_total=order_summary.grand_total)
        db.add(order)
        db.commit()
        
        for j in order_data:
            order_item = models.OrderItem(order_id=order.id,beverage_id=j.beverage_id,mrp=j.mrp,quantity=j.quantity,cases=j.cases,discount=j.discount,total_price=j.total_price)
            db.add(order_item)
        db.commit()
        return RedirectResponse(url='/orders?order_saved=True', status_code=303)

@router.post('/delete-order', response_class=HTMLResponse)
def delete_order(
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user), 
    order_id: Optional[int] = Form(None)
):
    if order_id:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order:
            db.delete(order)
            db.commit()
            return RedirectResponse(url="/orders?order_delete=True", status_code=303)
        else:
            return RedirectResponse(url='/orders')


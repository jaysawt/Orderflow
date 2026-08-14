from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, hash_password, verify_password, templates
from app.database import models

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def setup_page(request: Request, db: Session = Depends(get_db)):
    if db.query(models.User).first():
        return RedirectResponse(url='/login')

    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={}
    )

@router.post("/setup", response_class=HTMLResponse)
def setup_user(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.User).first():
        return RedirectResponse(url='/login')

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request, name="setup.html",
            context={"error": "Passwords do not match."}
        )
    
    user = models.User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse(url='/login?success=true', status_code=303)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: bool = False, success: bool = False, reset: bool = False):
    error_message = (
        "Invalid username or password. Please try again." if error
        else "Setup user successfully" if success
        else "Password reset successfully. Please log in with your new password." if reset
        else None
    )
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error_message}
    )

@router.post('/login', response_class=HTMLResponse)
def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login?error=true", status_code=303)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={}
    )

@router.post("/forgot-password", response_class=HTMLResponse)
def forgot_password_user(
    request: Request,
    username: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "User with this username does not exist."}
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={"error": "Passwords do not match."}
        )

    user.hashed_password = hash_password(new_password)
    db.commit()
    return RedirectResponse(url="/login?reset=true", status_code=303)
from app.database.database import Base, engine, SessionLocal
from app.database import models
from app.functions.auth import hash_password
from starlette.middleware.sessions import Session
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spirits Distribution Portal")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def setup_page(request: Request, db: Session = Depends(get_db)):
    if db.query(models.User).first():
        return RedirectResponse(url='/login')

    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={}
    )

@app.post("/setup", response_class=HTMLResponse)
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

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: bool = False, success: bool = False):
    error_message = "Invalid username or password. Please try again." if error else "Setup up user successfully" if success else None
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error_message}
    )

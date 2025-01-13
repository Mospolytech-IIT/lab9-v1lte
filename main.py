from fastapi import FastAPI, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import os
from database import Base, engine
from fastapi.responses import RedirectResponse


# Создаём все таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Указываем полный путь к папке с шаблонами
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def get_users(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse("users_list.html", {"request": request, "users": users})

@app.get("/users/create")
def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/users/create")
def create_user_view(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    crud.create_user(db, username, email, password)
    return RedirectResponse(url="/users", status_code=303)

@app.get("/users/edit/{user_id}")
def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.post("/users/edit/{user_id}")
def edit_user(user_id: int, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id, username, email, password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/users", status_code=303)

@app.get("/posts/")
def get_posts(request: Request, db: Session = Depends(get_db)):
    posts = crud.get_posts(db)
    return templates.TemplateResponse("posts_list.html", {"request": request, "posts": posts})

@app.get("/posts/create")
def create_post_form(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse("create_post.html", {"request": request, "users": users})

@app.post("/posts/create")
def create_post_view(title: str = Form(...), content: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    crud.create_post(db, title, content, user_id)
    return RedirectResponse(url="/posts", status_code=303)

@app.get("/posts/edit/{post_id}")
def edit_post_form(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post_by_id(db, post_id)
    users = crud.get_users(db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post, "users": users})


@app.post("/posts/edit/{post_id}")
def edit_post(post_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    post = crud.update_post(db, post_id, title, content)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return RedirectResponse(url="/posts", status_code=303)

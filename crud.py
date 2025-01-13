from sqlalchemy.orm import Session
from models import User, Post

# Функция для создания пользователя
def create_user(db: Session, username: str, email: str, password: str):
    db_user = User(username=username, email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Функция для получения всех пользователей
def get_users(db: Session):
    return db.query(User).all()

# Функция для получения пользователя по ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Функция для создания поста
def create_post(db: Session, title: str, content: str, user_id: int):
    db_post = Post(title=title, content=content, user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Функция для получения всех постов
def get_posts(db: Session):
    return db.query(Post).all()

# Функция для получения постов конкретного пользователя
def get_posts_by_user(db: Session, user_id: int):
    return db.query(Post).filter(Post.user_id == user_id).all()

# Функция для редактирования пользователя
def update_user(db: Session, user_id: int, username: str, email: str, password: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.username = username
        db_user.email = email
        db_user.password = password
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Функция для редактирования поста
def update_post(db: Session, post_id: int, title: str, content: str):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db_post.title = title
        db_post.content = content
        db.commit()
        db.refresh(db_post)
        return db_post
    return None

# Функция для получения поста по ID
def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

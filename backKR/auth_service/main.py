import pika
import json
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from .database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

# Настройка CORS


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (можно указать конкретные домены)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, OPTIONS и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)
# Создаем таблицы базы данных
models.Base.metadata.create_all(bind=engine)


# Настройка RabbitMQ для отправки сообщений
def send_message_to_queue(message: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='auth_events')
    channel.basic_publish(exchange='', routing_key='auth_events', body=json.dumps(message))
    connection.close()


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user.username)
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"sub": user.username})

    # Отправляем сообщение в RabbitMQ после успешного входа
    send_message_to_queue({"username": user.username, "event": "login_success"})

    return {"access_token": access_token, "token_type": "bearer"}

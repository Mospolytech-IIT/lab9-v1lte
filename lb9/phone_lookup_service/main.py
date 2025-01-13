import logging
from fastapi import FastAPI, Depends, HTTPException, Request, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, lookup, messaging
from .database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

# Инициализация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем таблицы базы данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (можно указать конкретные домены)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, OPTIONS и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# Настраиваем схему для передачи токена в заголовке
api_key_header = APIKeyHeader(name="Authorization")


def get_current_user(api_key: str = Security(api_key_header)):
    # Ожидаем формат "Bearer <token>", проверяем и убираем "Bearer "
    if not api_key.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    token = api_key.split(" ")[1]  # Извлекаем сам токен после "Bearer"

    user_id = messaging.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.post("/lookup", response_model=schemas.LookupResponse)
def lookup_number(
        request: schemas.LookupRequest,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    result = lookup.process_phone_number(db, request.phone_number)
    crud.create_lookup(db=db, lookup_data=request, user_id=current_user, result=result)
    return schemas.LookupResponse(phone_number=request.phone_number, result=result)


@app.get("/history", response_model=list[schemas.LookupResponse])
def get_lookup_history(
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    history = crud.get_lookups_by_user(db, user_id=current_user)
    return [schemas.LookupResponse(phone_number=record.phone_number, result=record.result) for record in history]


@app.delete("/delete-history")
def delete_lookup_history(
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    deleted_count = crud.delete_lookups_by_user(db, user_id=current_user)
    return {"deleted_records": deleted_count}


@app.post("/add-phone-owner", response_model=schemas.PhoneOwnerResponse)
def add_phone_owner(
        phone_owner: schemas.PhoneOwnerCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    existing_owner = crud.get_phone_owner_by_number(db, phone_owner.phone_number)
    if existing_owner:
        raise HTTPException(status_code=400, detail="Phone number already exists")

    new_owner = crud.create_phone_owner(db=db, phone_owner=phone_owner)
    return new_owner

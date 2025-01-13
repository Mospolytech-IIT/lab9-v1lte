from sqlalchemy import Column, Integer, String
from .database import Base

class PhoneLookup(Base):
    __tablename__ = "phone_lookups"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    user_id = Column(String)  # Хранение user_id из AuthService
    lookup_time = Column(String)  # Дата запроса
    result = Column(String)  # Информация по номеру телефона

class PhoneOwner(Base):
    __tablename__ = "phone_owners"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    owner_name = Column(String)  # Имя владельца
    additional_info = Column(String, nullable=True)  # Дополнительная информация

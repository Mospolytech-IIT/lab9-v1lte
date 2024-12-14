import re
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError, validator
from . import models, schemas

class ValidatedPhoneNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("Номер телефона должен быть строкой")
        if not re.match(r'^\d+$', v):
            raise ValueError("Номер телефона должен содержать только цифры")
        return v

class LookupRequest(BaseModel):
    phone_number: ValidatedPhoneNumber

class PhoneOwnerCreate(BaseModel):
    phone_number: ValidatedPhoneNumber
    owner_name: str
    additional_info: str

def create_lookup(db: Session, lookup_data: LookupRequest, user_id: str, result: str):
    try:
        validated_lookup_data = LookupRequest(phone_number=lookup_data.phone_number)
    except ValidationError as e:
        raise ValueError("Некорректный формат номера телефона") from e

    lookup_record = models.PhoneLookup(
        phone_number=validated_lookup_data.phone_number,
        user_id=user_id,
        lookup_time="2023-11-13",  # Вставьте актуальное время
        result=result
    )
    db.add(lookup_record)
    db.commit()
    db.refresh(lookup_record)
    return lookup_record

def get_lookups_by_user(db: Session, user_id: str):
    return db.query(models.PhoneLookup).filter(models.PhoneLookup.user_id == user_id).all()

def delete_lookups_by_user(db: Session, user_id: str):
    records_to_delete = db.query(models.PhoneLookup).filter(models.PhoneLookup.user_id == user_id)
    count = records_to_delete.delete(synchronize_session=False)
    db.commit()
    return count

def create_phone_owner(db: Session, phone_owner: PhoneOwnerCreate):
    db_phone_owner = models.PhoneOwner(
        phone_number=phone_owner.phone_number,
        owner_name=phone_owner.owner_name,
        additional_info=phone_owner.additional_info
    )
    db.add(db_phone_owner)
    db.commit()
    db.refresh(db_phone_owner)
    return db_phone_owner

def get_phone_owner_by_number(db: Session, phone_number: ValidatedPhoneNumber):
    try:
        validated_phone_number = ValidatedPhoneNumber.validate(phone_number)
    except ValidationError as e:
        raise ValueError("Некорректный формат номера телефона") from e

    return db.query(models.PhoneOwner).filter(models.PhoneOwner.phone_number == validated_phone_number).first()

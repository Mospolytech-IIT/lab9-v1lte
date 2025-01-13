from sqlalchemy.orm import Session
from . import crud


def process_phone_number(db: Session, phone_number: str) -> str:
    """
    Ищет информацию о владельце номера телефона в базе данных.
    Если информация найдена, возвращает данные о владельце.
    Если информация не найдена, возвращает сообщение о том, что данных нет.
    """
    # Ищем информацию о владельце по номеру телефона
    owner_info = crud.get_phone_owner_by_number(db, phone_number)
    if owner_info:
        result = f"Owner: {owner_info.owner_name}, Additional Info: {owner_info.additional_info or 'N/A'}"
    else:
        result = "No information available for this phone number."

    return result

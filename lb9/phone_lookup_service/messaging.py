from jose import JWTError, jwt

SECRET_KEY = "your_secret_key"  # Замените на ваш секретный ключ
ALGORITHM = "HS256"

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

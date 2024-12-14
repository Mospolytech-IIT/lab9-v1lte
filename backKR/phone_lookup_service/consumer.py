import pika
import json
from . import database
from sqlalchemy.orm import Session
from .database import SessionLocal

def process_login_event(username: str):
    db: Session = SessionLocal()
    try:
        print(f"User {username} logged in successfully.")
    finally:
        db.close()

def callback(ch, method, properties, body):
    message = json.loads(body)
    if message["event"] == "login_success":
        process_login_event(message["username"])

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='auth_events')
    channel.basic_consume(queue='auth_events', on_message_callback=callback, auto_ack=True)
    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    consume()

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]


# Створення сесії для роботи з БД
def session_create(db_path=None, **kwargs):
    pb_path = db_path or DATABASE_URL
    engine = create_engine(pb_path, echo=True)
    session = sessionmaker(bind=engine, autoflush=False)
    return session()

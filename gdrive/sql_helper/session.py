from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL


# Створення сесії для роботи з БД
def session_create(db_path=None, **kwargs):
    pb_path = db_path or DATABASE_URL
    engine = create_engine(pb_path, echo=True)
    session = sessionmaker(bind=engine, autoflush=False)
    return session()

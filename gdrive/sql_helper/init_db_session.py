import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
BASE = declarative_base()


def start():
    try:
        engine = create_engine(DATABASE_URL)
        BASE.metadata.bind = engine
        BASE.metadata.create_all(engine)
        return scoped_session(sessionmaker(bind=engine, autoflush=False))
    except ValueError:
        print('Invalid DATABASE_URL : Exiting now.')


SESSION = start()

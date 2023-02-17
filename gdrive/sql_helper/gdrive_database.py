import pickle

from sqlalchemy import create_engine, Column, LargeBinary
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql.sqltypes import BigInteger

from session import DATABASE_URL


class Base(DeclarativeBase): pass


class GDriveCreds(Base):
    __tablename__ = "gdrive"
    chat_id = Column(BigInteger, primary_key=True)
    credential_string = Column(LargeBinary)


# Для створення талиць у БД запустіть файл, як "main"
if __name__ == "__main__":
    engine = create_engine(DATABASE_URL, echo=True)
    session = sessionmaker(bind=engine, autoflush=False)()
    Base.metadata.create_all(engine)
    session.commit()

import os
import pickle

from sqlalchemy import create_engine, Column, LargeBinary
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql.sqltypes import BigInteger
from .session import session_create


# from session import DATABASE_URL


class Base(DeclarativeBase): pass


class GDriveCreds(Base):
    __tablename__ = "gdrive"
    user_id = Column(BigInteger, primary_key=True)
    credential_string = Column(LargeBinary)


async def set_cred(user_id, cred):
    my_session = session_create()
    saved_cred = my_session.query(GDriveCreds).get(user_id)
    if not saved_cred:
        saved_cred = GDriveCreds(user_id=user_id)

    # saved_cred = GDriveCreds(user_id=user_id, credential_string=pickle.dumps(cred))
    saved_cred.credential_string = pickle.dumps(cred)
    my_session.add(saved_cred)  # добавляем в бд
    my_session.commit()  # сохраняем изменения
    my_session.refresh(saved_cred)


def get_creds(chat_id):
    session = session_create()
    saved_cred = session.query(GDriveCreds).get(chat_id)
    return (
        pickle.loads(saved_cred.credential_string)
        if saved_cred is not None
        else None
    )


# Для створення талиць у БД запустіть файл, як "main"
if __name__ == "__main__":
    engine = create_engine(os.environ["DATABASE_URL"], echo=True)
    create_table_session = sessionmaker(bind=engine, autoflush=False)()
    Base.metadata.create_all(engine)
    create_table_session.commit()

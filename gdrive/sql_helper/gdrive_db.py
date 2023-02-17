import pickle

from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.sql.sqltypes import BigInteger
from gdrive.sql_helper.init_db_session import BASE, SESSION


class GDriveCreds(BASE):
    __tablename__ = "gdrive"
    chat_id = Column(BigInteger, primary_key=True)
    credential_string = Column(LargeBinary)

    def __init__(self, chat_id):
        self.chat_id = chat_id

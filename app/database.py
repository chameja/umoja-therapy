import os

from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv

load_dotenv()

mysql_url = os.getenv("DATABASE_URL")
engine = create_engine(mysql_url, echo=True) 

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as db_session:
        yield db_session

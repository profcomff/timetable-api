import os
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from pydantic.networks import PostgresDsn

load_dotenv()


class Settings(BaseModel):
    DB_DSN: PostgresDsn = os.getenv("DB_DSN")

    class Config:
        env_file = '.env'


settings = Settings()


def connect(table_name):
    engine = create_engine(f"{settings.DB_DSN}", echo=True)
    meta = MetaData(engine)
    tablepython = Table(table_name, meta, autoload = True)

    try:
        engine.connect()
        print('Connection successful')
    except SQLAlchemyError as e:
        print(f"The error '{e}' occurred")
    return tablepython, engine


timetable, engine = connect('timetable')

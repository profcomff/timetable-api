import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")


def connect():
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True)

    meta = MetaData(engine)

    timetable = Table('timetable', meta, autoload=True)

    try:
        engine.connect()
        print('Connection successful')
    except SQLAlchemyError as e:
        print(f"The error '{e}' occurred")
    return timetable, engine


timetable, engine = connect()

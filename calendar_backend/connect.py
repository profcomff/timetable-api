from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from settings import Settings

settings = Settings()


def connect(table_name):
    engine = create_engine(f"{settings.DB_DSN}", echo=True)
    meta = MetaData(engine)
    tablepython = Table(table_name, meta, autoload=True)

    try:
        engine.connect()
        print('Connection successful')
    except SQLAlchemyError as e:
        print(f"The error '{e}' occurred")
    return tablepython, engine


timetable, engine = connect(settings.TIMETABLE_NAME)

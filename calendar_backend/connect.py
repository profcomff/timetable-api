import keyring
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, MetaData, Table

DB_USER = 'grigorevsi'
system = 'app'
DB_HOST = 'db.profcomff.com'
DB_NAME = 'dev'
DB_PORT = '25432'


def get_pass(system: str, username: str):
    return keyring.get_password(system, username)


DB_PASS = get_pass("app", "grigorevsi")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True)

meta = MetaData(engine)

timetable = Table('timetable', meta, autoload=True)

try:
    conn = engine.connect()
    print('Connection successful')
except SQLAlchemyError as e:
    print(f"The error '{e}' occurred")


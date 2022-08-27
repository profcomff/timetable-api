import logging

import uvicorn
from calendar_backend.models.db import Event

from calendar_backend.routes import app
from calendar_backend.settings import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    filename=f'logger_{__name__}.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

if __name__ == "__main__":
    settings = get_settings()
    e = create_engine(settings.DB_DSN, echo=True)
    Session = sessionmaker(e)
    session = Session()
    event = Event.get(26, session=session)
    for comment in event.comments:
        print(comment)

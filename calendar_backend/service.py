from multiprocessing import connection
import pickle
import os.path
import json

import google.oauth2.credentials
import googleapiclient.discovery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from db import Credentials
from settings import Settings

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
settings = Settings()
connection = create_engine(settings.DB_DSN)
db = sessionmaker(bind=connection)()


def get_calendar_service(id: int) -> googleapiclient.discovery.Resource:
    try:
        user_data = db.query(Credentials).filter_by(id=id).one()
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(user_data.token), SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except NoResultFound:
        print(f'service for id {id} not found in db')


def get_calendar_service_from_token(token) -> googleapiclient.discovery.Resource:
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(token), SCOPES)
    return build('calendar', 'v3', credentials=credentials)


if __name__ == '__main__':
    print(get_calendar_service(44))

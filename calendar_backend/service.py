from multiprocessing import connection
import pickle
import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

from db import Credentials
from settings import Settings

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
settings = Settings()
connection = create_engine(settings.DB_DSN)
db = sessionmaker(bind=connection)()

def get_calendar_service(id: int):
    user_data = db.query(Credentials).filter_by(id = id).one()
    flow = Flow.from_client_secrets_file(
        './env/client_secret.json', 
        user_data.scope,
        redirect_uri = "http://localhost:8000/credentials"
    )
    print(user_data.code)
    flow.fetch_token(code = user_data.code)
    session = flow.authorized_session()
    #service = build('calendar', 'v3', credentials=creds)
    #return service

if __name__ == '__main__':
    print(get_calendar_service(42))
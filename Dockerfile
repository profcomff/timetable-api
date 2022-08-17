FROM python:3.10
WORKDIR /app

COPY ./gunicorn_conf.py /app/gunicorn_conf.py
COPY ./requirements.txt /app/
COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY ./calendar_backend /app/calendar_backend

RUN mkdir cache && pip install --no-cache-dir -r /app/requirements.txt
CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "calendar_backend.routes.base:app" ]

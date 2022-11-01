FROM python:3.10
WORKDIR /app
RUN mkdir -p static/cache && mkdir -p static/photo/lecturer

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

ADD gunicorn_conf.py alembic.ini /app/
ADD migrations /app/migrations
ADD calendar_backend /app/calendar_backend

VOLUME ["/app/static"]

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "calendar_backend.routes.base:app" ]

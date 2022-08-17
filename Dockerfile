FROM python:3.10
WORKDIR /app

COPY ./requirements.txt /app/
COPY ./gunicorn_conf.py /app/gunicorn_conf.py
COPY ./calendar_backend /app/calendar_backend

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN mkdir cache
ENTRYPOINT [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py", "calendar_backend.routes.base:app" ]

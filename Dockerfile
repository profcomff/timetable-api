FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
WORKDIR /calendar_backend
RUN uvicorn app:app --reload
WORKDIR ".."

COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt  && mkdir /app/static

COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY ./templates /app/templates
COPY ./${APP_NAME} /app/${APP_NAME}

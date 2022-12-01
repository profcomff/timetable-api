FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
ENV APP_NAME=calendar_backend
ENV APP_MODULE=${APP_NAME}.routes.base:app

COPY ./requirements.txt /app/
RUN pip install -U -r /app/requirements.txt

COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations/
COPY ./static /static/
COPY ./${APP_NAME} /app/${APP_NAME}

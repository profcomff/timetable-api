FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
ENV APP_NAME=calendar_backend
ENV APP_MODULE=${APP_NAME}.routes.base:app

COPY ./requirements.txt /app/
RUN pip install -U -r /app/requirements.txt

COPY ./static /app/static/

COPY ./alembic.ini /alembic.ini
COPY ./logging_prod.conf /app/
COPY ./logging_test.conf /app/
COPY ./migrations /migrations/

COPY ./${APP_NAME} /app/${APP_NAME}

# timetable-backend
Бэкэнд сервиса расписания студентов физфака

# Установка
## Google API
* Чтобы подключить Google API, нужно создать приложение в google cloud console , получить client_secret.json
и закинуть его в репозиторий

* https://developers.google.com/calendar/api/quickstart/python

## dotenv
* Переименовать `.env.example` в `.env`
* Внести в `.env` корректные переменные окружения

## Запуск
```console
foo@bar:~$ python3 -m venv venv
foo@bar:~$ pip install -r requirements.txt
foo@bar:~$ uvicorn --reload --log-level debug calendar_backend.routes.base:app
```

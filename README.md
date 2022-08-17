# timetable-backend
Бэкэнд сервиса расписания студентов физфака

# Установка
## Google API
* Чтобы подключить Google API, нужно создать приложение в google cloud console , получить client_secret.json
и закинуть его в репозиторий вместо example_secret.json

* https://developers.google.com/calendar/api/quickstart/python

## dotenv
* Переименовать `.env.example` в `.env`
* Внести в `.env` корректные переменные окружения

## Запуск
* `python3 -m calendar_backend`
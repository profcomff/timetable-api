## Что нужно для запуска 

1. python3.11. Установка описана [тут](https://www.python.org/downloads/)

2. Docker. Как установить docker описано [тут](https://docs.docker.com/engine/install/)

3. PostgreSQL. Запустить команду
```console
docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-timetable_api postgres:15
```

## Какие переменные нужны для запуска
- `DB_DSN=postgresql://postgres@localhost:5432/postgres`


## Codestyle

- Black. Как пользоваться описано [тут](https://black.readthedocs.io/en/stable/)

- Также применяем [isort](https://pycqa.github.io/isort/)


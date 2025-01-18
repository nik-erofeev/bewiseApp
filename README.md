

# Установка и запуск
Создайте в корне приложения файл **.env** и определите в нём все переменные, указанные в [.env_example](./.env_example).

## Запуск через docker-compose

#### Собрать и запустить/остановить приложение с помощью
```sh
$ make up
$ make up_re

$ make down
```



#### Перейти на swagger [http://localhost:8000/](http://localhost:8000)
```sh
http://localhost:8000/
```

<br>

#### Перейти на веб интерфейс kafka (topik) [http://localhost:8090](http://localhost:8090)
```sh
http://localhost:8090
```

<br>

#### запуск в отдельном в контейнере, при этом должны должны быть подняты (kafka/redis/postgres)
```shell
make docker_test
```


## Локально
#### Загрузить ЕНВы из файла .env(при локальном  смотреть коммент в [.env_example](./.env_example))

#### Установить и активировать виртуальное окружение с помощью команд:
```sh
$ python3.12 -m venv venv
$ source venv/bin/activate
```

#### Установить зависимости:
```sh
$ pip install poetry
$ poetry install
```

 +- может понадобиться

```sh
$ mypy --install-types
```

<br>



#### Запустить/остановить контейнеры кроме API:
```sh
$ make up_local
$ make down
```



<br>

#### Прогнать миграции с помощью с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/):
```sh
$ alembic upgrade head
```


#### Запустить приложение с помощью:
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

<br>

#### Перейти на swagger [http://localhost:8000/](http://localhost:8000)
```sh
http://localhost:8000/
```

<br>

#### Перейти на веб интерфейс kafka (topik) [http://localhost:8090](http://localhost:8090)
```sh
http://localhost:8090
```

<br>

#### Тесты

#### запуск в отдельном в контейнере, при этом должны должны быть подняты (kafka/redis/postgres)
```shell
make docker_test
```

#### при локально запуске тестов переопределить **Env** на локальные(host/port)

```shell
make pytest
```

<br>
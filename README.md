# data-loader-backend
## Описание
Содержит consumer kafka и Django приложение для предоставления API.

## Kafka consumer
### Описание
Потребляет сообщения из kafka, записывает их в TimescaleDB, в кэш Redis и отправляет
по redis pubsub в realtime-backend
### Запуск
```shell
poetry install
python manage.py start_data_load
```

## Django
### Описание
Web-приложения для предоставления доступа к данным посредством http.
### Запуск
```shell
poetry install
python manage.py migrate
python manage.py runserver
```
### Доступ к API
http://localhost:8000
## Сборка docker-образа
```shell
docker build --target production --tag data-loader-backend:latest .
```

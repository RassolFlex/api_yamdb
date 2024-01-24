# API для YAMDb

## Описание
REST API для веб-сайта с базами данных о произведениях кинематографа, музыки и литературы.


## Примеры
Вся документация API с примерами запросов находится по адресу - http://127.0.0.1:8000/redoc/

***

Использованный стек технологий:
- Python
- SQLite
- Django
- Drango REST Framework
- DRF SimpleJWT

***

## Установка
1. Склонируйте репозиторий на локальную машину с помощью команды `git clone`.

2. Создайте виртуальную среду, активируйте её и установите зависимости выполнив следующие команды:


```
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

3. Создайте и примените миграции выполнив следующие команды:

```
python manage.py makemigrations
python manage.py migrate
```

4. Запустите сервер:

```
python manage.py runserver
```

***

Авторы проекта:

Александр Огольцов
GitHub: `https://github.com/RassolFlex`

Антон Арефин
GitHub: `https://github.com/R4zeel`

Артём Дириженко
GitHub: `https://github.com/DEKATE33`
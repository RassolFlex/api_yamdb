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

4. Заполните БД тестовыми данными выполнив следующие команды:

```
python manage.py csv_import
python manage.py loaddata data.json
```

5. Запустите сервер:

```
python manage.py runserver
```

## Примеры использования

### Получение токена

Перед началом использования API необходимо создать пользователя и получить для него токен.

1. Создайте пользователя выполнив следующую команду:

```
python manage.py createsuperuser
```

2. Для получения кода подтверждения необходимо отправить POST-запрос на `http://127.0.0.1/api/v1/auth/signup/` со следующим содержимым:

```
{
    "username": "<*ваш_username*>",
    "email": "<*ваш_email*>"
}
```

**Примечание**:
Код подтверждения будет отправлен в теле письма на email пользователя. По умолчанию письма сохраняется в папке проекта `../send_mail/`.

3. Для получения токена необходимо отправить POST-запрос на `http://127.0.0.1/api/v1/auth/token/` со следующим содержимым:

```
{
    "username": "<*ваш_username*>",
    "confirmation_code": "<*ваш_confirmation_code_из_письма*>"
}
```

***

## Примеры запросов

### Просмотр произведений
Для просмотра списка всех произведений отправьте GET-запрос на `http://127.0.0.1:8000/api/v1/titles/`.

### Создание отзывов
Для создания нового отзыва на произведение отправьте POST-запрос на `http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/` со следующим содержимым:

```
{
    "text": "<*текст_отзыва*>",
    "score": <*целочисленное_значение_от_1_до_10*>
}
```

**Примечание**:
При запросах к API не забудьте указать токен.

### Создание комментариев
Для создания комментария отправьте POST-запрос на `http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/` со следующим содержимым:

```
{
    "text": "<*текст_комментария*>"
}
```

### Изменение комментариев
Для изменения комментария отправьте PUTCH-запрос на `http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` со следующим содержимым:

```
{
    "text": "<*текст_комментария*>"
}
```

### Просмотр своей учётной записи пользователя
Для просмотра своей учётной записи отправьте GET-запрос на `http://127.0.0.1:8000/api/v1/users/me/`.

***

Авторы проекта:

Александр Огольцов
GitHub: `https://github.com/RassolFlex`

Антон Арефин
GitHub: `https://github.com/R4zeel`

Артём Дириженко
GitHub: `https://github.com/DEKATE33`

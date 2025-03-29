FastAPI Audio Upload Service
Этот сервис позволяет пользователям загружать аудиофайлы с авторизацией через Яндекс. Файлы хранятся локально, а база данных PostgreSQL используется для управления пользователями.

Tехнологии
FastAPI — асинхронный API-фреймворк

SQLAlchemy (async) — ORM для работы с PostgreSQL

Docker — контейнеризация

JWT — внутренняя аутентификация API

OAuth2 (Яндекс) — авторизация

bash '''
git clone https://github.com/your-repo.git
cd your-repo

'''
.env file
bash '''
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/audio_db
YANDEX_CLIENT_ID=your_client_id
YANDEX_CLIENT_SECRET=your_client_secret
YANDEX_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
SECRET_KEY=your_secret_key
ALGORITHM=HS256

'''

Docker:

bash '''
docker-compose up --build

'''

Authorisation:
bash '''
http://127.0.0.1:8000/auth/login

'''

API Эндпоинты

Авторизация
Метод	Эндпоинт	Описание
GET	/auth/login	Перенаправление на Яндекс OAuth
GET	/auth/callback	Обработка OAuth-кода и выдача api_token
GET	/auth/refresh_token	Обновление api_token

Работа с пользователями
Метод	Эндпоинт	Описание
GET	/auth/users/me	Получение данных текущего пользователя

Загрузка аудиофайлов
Метод	Эндпоинт	Описание
POST	/auth/upload-audio/	Загрузка аудиофайла
# Классификация текста и статей 

## Описание 
Сервис автоматической классификации текстов (статей) по 10 тематическим категориям на основе дообученной модели **ruModernBERT**.
Сервис принимает текст или ссылку на статью, асинхронно обрабатывает запрос и возвращает предсказанный класс. Поддерживаются русскоязычные тексты.

## Архитектура:
- FastAPI — API
- Celery + RabbitMQ — очередь задач
- Redis — кэширование
- PostgreSQL — хранение статусов задач
- Nginx — статика и reverse proxy
- Docker — контейнеризация

## Технологии

- **Backend:** FastAPI 
- **ML:** PyTorch, Hugging Face Transformers (ruModernBERT)
- **Очереди:** Celery, RabbitMQ
- **Базы данных:** PostgreSQL, Redis
- **Веб-сервер:** Nginx
- **Контейнеризация:** Docker, Docker Compose
- **Парсинг:** aiohttp, BeautifulSoup4

## 🚀 Быстрый старт
### 1. Клонирование репозитория

```bash
git clone https://github.com/lmalborought/Diplom.git
cd Diplom
```
### 2. Скачайте модель по ссылке https://disk.yandex.ru/d/Qd5ezbkaU2_SiQ

### 3. Поместите скачанный файл model_weights.pt в корень проекта

### 4. Создайте файл .env в корне проекта:
   ```bash
# .env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
DB_NAME=app

DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

DEBUG=False

HF_TOKEN=your_huggingface_token_here

REDIS_URL=redis://redis:6379/0
   ```
- Замените your_password на надежный пароль, а your_huggingface_token_here — на ваш личный токен HuggingFace
  
### 5. Запустить
```bash
docker-compose up -d --build
```
## Интерфейс
### Ввод текста
![](images/text.png)

### Ввод ссылки
![](images/link.png)

## API
- POST /api/predict/text — классификация текста

- POST /api/predict/url — классификация статьи по ссылке

- GET /api/predict/task/{task_id} — статус задачи

## 🔗 Доступ к сервису (локально)

После запуска сервис будет доступен по следующим адресам:

| Сервис | Адрес | Описание |
|--------|-------|----------|
| Веб-интерфейс | `http://localhost` | Главная страница |
| Flower (мониторинг Celery) | `http://localhost:5555` | Статус задач и воркеров |
| RabbitMQ Management | `http://localhost:15672` | Интерфейс брокера (guest/guest) |


## Структура проекта

```
text-classification/                       
│
├── docker-compose.yml
├── requirements.txt
│
├── alembic/                          # Миграции БД
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── e7dde0c052d3_create_task_status_table.py
│       ├── b51aac07fd4f_add_task_statuses_table.py
│       └── f0b90ecb49e3_create_articles_table.py
│
├── app/                              # Основная папка бэкенда
├── main.py                 # Точка входа приложения: создание FastAPI/роуты/подключение всего
├── config.py               # Конфигурация (переменные окружения, настройки приложения/БД и т.п.)
├── database.py             # Подключение к БД: engine/session, базовые настройки ORM
├── task.py                 # Фоновые задачи/очереди (Celery)
├── Dockerfile              # Сборка Docker-образа бэкенда
│
├── api/                    # HTTP API-слой (роуты/эндпоинты)
│   ├── __init__.py         # Инициализация пакета
│   └── predict.py          # Эндпоинты для предсказания/инференса
│
├── models/                 # ORM-модели таблиц БД
│   ├── __init__.py
│   ├── article.py          # Модель Article (статьи)
│   └── status.py           # Модель Status (статусы задач/обработки)
│
├── schemas/                # Pydantic-схемы (валидация/формат запросов и ответов)
│   ├── __init__.py
│   └── predict.py          # Схемы для predict: request/response
│
├── services/               # Бизнес-логика (не завязана на HTTP)
│   ├── __init__.py
│   ├── inference.py        # Инференс модели/предсказания
│   └── parser.py           # Парсинг/подготовка данных (например текстов/статей)
│
└── crud/                   # Доступ к данным (CRUD-операции по сущностям)
  ├── __init__.py
  ├── article.py          # CRUD для Article
  └── status.py           # CRUD для Status                        
└── frontend/
  ├── Dockerfile
  ├── index.html
  ├── css/
  │   └── style.css
  └── js/
      └── script.js                              
```


## Архитектура
![](images/scheme.png)

# Классификация текста и статей 

## Структура проекта

```
text-classification/                       
│
├── docker-compose.yml
├── requirements.txt
│
├── k8s/                              # Kubernetes манифесты
│   ├── backend.yaml
│   ├── celery.yaml
│   ├── frontend.yaml
│   ├── ingress.yaml
│   ├── namespace.yaml
│   ├── postgres.yaml
│   └── redis.yaml
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



## API

- `POST /predict/text`

![](images/img.png)
- `POST /predict/url` 

![](images/img_1.png)
----
### 1. Клонирование репозитория

```bash
git clone https://github.com/lmalborought/Diplom.git
```
### 2. Скачайте модель по ссылке https://disk.yandex.ru/d/UYUM1T_MXVxB5Q
### 3. Поместите скачанный файл 0.8323_best_model_BERT.pt в корень проекта
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

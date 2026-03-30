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

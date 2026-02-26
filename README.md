# Text Classification

Классификация текста и статей 

## Структура проекта

```
text_classification/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация (БД, пути)
│   ├── database.py          # Подключение к БД
│   ├── models.py            # Модели SQLAlchemy (Article)
│   ├── crud.py              # Операции с БД (save_article, get_article_by_id)
│   ├── schemas.py           # Pydantic модели (PredictResponse, URLRequest)
│   ├── parser.py            # Парсинг статей по URL
│   ├── inference.py         # ML модель (BERT)
│   └── static/
│       └── index.html       # Фронтенд
├── 0.8323_best_model_BERT.pt   # Веса модели
├── requirements.txt
├── run.py                   # python run.py
└── README.md
```


## API

- `POST /predict/text`

![](images/img.png)
- `POST /predict/url` 

![](images/img_1.png)

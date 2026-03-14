# Text Classification

Классификация текста и статей 

## Структура проекта

```
app/
├── __init__.py
├── main.py              # создание приложения, lifespan, CORS, подключение роутеров
├── config.py
├── database.py
├── api/
│   ├── __init__.py      # api_router, подключение роутов
│   └── predict.py       # эндпоинты /predict/text, /predict/url
├── models/
│   ├── __init__.py
│   └── article.py       # модель Article
├── schemas/
│   ├── __init__.py
│   └── predict.py       # PredictResponse, URLRequest
├── services/
│   ├── __init__.py
│   ├── inference.py     # InferenceService
│   └── parser.py        # парсинг статей, data_cleaning, data_prep
├── crud/
│   ├── __init__.py
│   └── article.py       # get_article_by_id, save_article
└── Dockerfile
├── frontend/
│   └── css/
│       └── style.css     
│   └── js/
│       └── script.js
│   ├── index.html 
├── 0.8323_best_model_BERT.pt   # Веса модели
└── requirements.txt
```


## API

- `POST /predict/text`

![](images/img.png)
- `POST /predict/url` 

![](images/img_1.png)

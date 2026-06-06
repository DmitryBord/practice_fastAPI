# Парсер сайта биржи(СПБСТсБ) и API для получения данных

Этот код разделен на два приложения:
1. spimex_app
    - Парсит сайт биржи `spimex.com` и сохраняет результаты торгов в базу данных
2. api_app
    - Предоставляет ручки для получения данных, сохраненных в базе данных


## Технологии которые использовались

1. api_app
    - FastAPI
    - pydantic
    - Redis

2. spimex_app
   - asyncio
   - bs4
   - curl_cffi
   - pandas
   - pdfplumber
   - SQLAlchemy

## Запуск проекта
1. Создаем файл `.env` в корневом каталоге проекта и заполняем его по шаблону из `example_env`
2. `alembic upgrade head` - Запускаем миграции БД
3. `python -m spimex_app.main` - Запускаем парсер для наполнения БД данными (работа парсера около 10 минут)
   - Если нужно собрать не все данные, то по пути `spimex_app/extract/parser` нужно изменить значение перменной `N`
   обозначающее количество страниц который парсер будет обрабатывать
4. Запускаем redis через докер:
   - `docker run -d --name redis -p 6379:6379 redis:7-alpine`
5. `python -m api_app.main` - Запускаем API приложение

# API Документация

## Получение последних торговых дат

Возвращает список последних торговых дней.

### Endpoint

```http
GET /spimex/trading-results/dates
```

### Query Parameters

| Параметр   | Тип     | Обязательный | Описание                                            |
| ---------- | ------- | ------------ | --------------------------------------------------- |
| count_days | integer | Нет          | Количество последних торговых дней. По умолчанию: 1 |

### Пример запроса

```http
GET /spimex/trading-results/dates?count_days=3
```

### Пример ответа

```json
[
  "2025-01-15",
  "2025-01-14",
  "2025-01-13"
]
```

---

## Получение последних торгов

Возвращает результаты последних торгов с возможностью фильтрации.

### Endpoint

```http
GET /spimex/trading-results
```

### Query Parameters

| Параметр          | Тип     | Обязательный | Описание          |
| ----------------- | ------- | ------------ | ----------------- |
| oil_id            | string  | Нет          | Код нефтепродукта |
| delivery_type_id  | string  | Нет          | Тип поставки      |
| delivery_basis_id | string  | Нет          | Базис поставки    |
| offset            | integer | Нет          | Смещение выборки  |
| limit             | integer | Нет          | Размер страницы   |

### Пример запроса

```http
GET /spimex/trading-results?oil_id=A100&limit=5
```

### Пример ответа

```json
[
  {
    "exchange_product_id": "A100NPTA",
    "exchange_product_name": "Бензин АИ-100",
    "oil_id": "A100",
    "delivery_basis_id": "NPT",
    "delivery_basis_name": "НПТ",
    "delivery_type_id": "A",
    "volume": 1000,
    "total": "15000000",
    "count": 10,
    "date": "2025-01-15"
  }
]
```

---

## Получение динамики торгов

Возвращает результаты торгов за указанный период.

### Endpoint

```http
GET /spimex/trading-results/dynamic
```

### Query Parameters

| Параметр          | Тип     | Обязательный | Описание                            |
| ----------------- | ------- | ------------ |-------------------------------------|
| start_date        | date    | Да           | Начальная дата периода (YYYY-MM-DD) |
| end_date          | date    | Да           | Конечная дата периода  (YYYY-MM-DD) |
| oil_id            | string  | Нет          | Код нефтепродукта                   |
| delivery_type_id  | string  | Нет          | Тип поставки                        |
| delivery_basis_id | string  | Нет          | Базис поставки                      |
| offset            | integer | Нет          | Смещение выборки                    |
| limit             | integer | Нет          | Размер страницы                     |


### Пример запроса

```http
GET /spimex/trading-results/dynamic?oil_id=A100&start_date=2025-01-01&end_date=2025-01-31
```

### Пример ответа

```json
[
  {
    "exchange_product_id": "A100NPTA",
    "exchange_product_name": "Бензин АИ-100",
    "oil_id": "A100",
    "delivery_basis_id": "NPT",
    "delivery_basis_name": "НПТ",
    "delivery_type_id": "A",
    "volume": 1200,
    "total": "18000000",
    "count": 12,
    "date": "2025-01-01"
  }
]
```

 
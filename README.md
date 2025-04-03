# Gosu CH API

Асинхронная библиотека для работы с CH API на Python.

## Основные возможности

- Отправка одиночных событий в CH
- Пакетная отправка событий
- Отправка данных в конкретную таблицу
- Настраиваемые эндпоинты API

## Установка

```bash
pip install git+github.com/alridev/py-ch-api
```

## Примеры использования

### Создание клиента

```python
from pychapi import ChClient
from pychapi.models import ChEndpoints

# Создание клиента с настройками по умолчанию
client = ChClient(
    base_url="http://localhost:8080",
    setter_token="setter-token",
    getter_token="getter-token",
    timeout=30.0,  # опционально
)

# Создание клиента с пользовательскими эндпоинтами
custom_endpoints = ChEndpoints(
    setter_many="/custom/many",
    setter_by_table="/custom/%s",
    setter_one="/custom/one"
)

client = ChClient(
    base_url="http://localhost:8080",
    setter_token="setter-token",
    getter_token="getter-token",
    endpoints=custom_endpoints,
)
```

### Отправка одного события

```python
from gosu_ch_api.models import SetterEvent

event = SetterEvent(
    table_name="events",
    data={"field": "value"}
)

try:
    await client.setter_one(event)
except ValueError as e:
    print(f"Ошибка: {e}")
```

### Пакетная отправка

```python
events = [
    SetterEvent(
        table_name="events",
        data={"field": "value"}
    ),
    SetterEvent(
        table_name="events",
        data={"field": "another_value"}
    ),
]

errors = await client.setter_many(events)
if errors:
    for index, error in errors.items():
        print(f"Ошибка в событии {index}: {error}")
```

### Отправка в конкретную таблицу

```python
try:
    await client.setter_by_table(
        table_name="events",
        data={"field": "value"}
    )
except ValueError as e:
    print(f"Ошибка: {e}")
```

## Структуры данных

### SetterEvent

```python
class SetterEvent:
    table_name: str  # Имя таблицы в CH
    data: Dict[str, Any]  # Данные для отправки
```

### ChEndpoints

```python
class ChEndpoints:
    setter_many: str = "/setter/many"  # Путь для пакетной отправки
    setter_by_table: str = "/setter/%s"  # Путь для отправки в таблицу
    setter_one: str = "/setter"  # Путь для отправки одного события
```

## Обработка ошибок

- Методы `setter_one` и `setter_by_table` выбрасывают `ValueError` при ошибке сервера
- Метод `setter_many` возвращает словарь с ошибками по индексам событий
- Все методы могут выбрасывать `aiohttp.ClientError` при ошибках сети 
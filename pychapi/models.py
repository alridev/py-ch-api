"""
Модели данных для работы с CH API
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SetterEvent(BaseModel):
    """Модель для отправки одного события"""
    table_name: str = Field(..., description="Имя таблицы в CH")
    data: Dict[str, Any] = Field(..., description="Данные для отправки")


class SetterRequestBody(BaseModel):
    """Модель для пакетной отправки событий"""
    events: List[SetterEvent] = Field(..., description="Список событий для отправки")


class SetterResponseBody(BaseModel):
    """Базовая структура ответа с ошибками"""
    errors: Dict[int, str] = Field(default_factory=dict, description="Ошибки по индексам")


class SetterManyResponseBody(SetterResponseBody):
    """Ответ на пакетную отправку"""
    pass


class SetterByTableResponseBody(BaseModel):
    """Ответ на отправку в конкретную таблицу"""
    error: Optional[str] = Field(None, description="Текст ошибки")


class SetterOneResponseBody(BaseModel):
    """Ответ на отправку одного события"""
    error: Optional[str] = Field(None, description="Текст ошибки")


class ChEndpoints(BaseModel):
    """Пути к эндпоинтам API"""
    setter_many: str = Field("/setter/many", description="Путь для пакетной отправки")
    setter_by_table: str = Field("/setter/%s", description="Путь для отправки в таблицу")
    setter_one: str = Field("/setter", description="Путь для отправки одного события") 
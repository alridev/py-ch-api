"""
Асинхронный клиент для работы с CH API
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import aiohttp
from pydantic import BaseModel

from .models import (
    ChEndpoints,
    SetterEvent,
    SetterManyResponseBody,
    SetterRequestBody,
)

T = TypeVar('T')

class ChClient:
    """Клиент для работы с CH API"""

    def __init__(
        self,
        base_url: str,
        setter_token: str,
        getter_token: str,
        endpoints: Optional[ChEndpoints] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Инициализация клиента

        Args:
            base_url: Базовый URL API
            setter_token: Токен для отправки данных
            getter_token: Токен для получения данных
            endpoints: Настройки путей API (если None, используются значения по умолчанию)
            timeout: Таймаут для запросов в секундах
        """
        self.base_url = base_url.rstrip("/")
        self.setter_token = setter_token
        self.getter_token = getter_token
        self.endpoints = endpoints or ChEndpoints(
            setter_one="/setter",
            setter_many="/setter/many",
            setter_by_table="/setter/%s",
        )
        self.timeout = timeout
        self.background = ChClientBackground(self)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[BaseModel, Dict[str, Any]]] = None,
        token: Optional[str] = None,
    ) -> Any:
        """
        Выполнение HTTP запроса

        Args:
            method: HTTP метод
            endpoint: Конечная точка API
            data: Данные для отправки (BaseModel или словарь)
            token: Токен авторизации

        Returns:
            Ответ от API

        Raises:
            aiohttp.ClientError: При ошибке выполнения запроса
            ValueError: При неверном статусе ответа
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        } if token else {"Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{self.base_url}/{endpoint.lstrip('/')}",
                json=data.model_dump() if isinstance(data, BaseModel) else data,
                headers=headers,
                timeout=self.timeout,
            ) as response:
                if response.status != 200:
                    response_data = await response.json()
                    if "errors" in response_data:
                        return response_data
                    raise ValueError(f"Server error: {response_data.get('error', 'Unknown error')}")
                return await response.json()

    async def setter_one(self, event: SetterEvent) -> None:
        """
        Отправка одного события

        Args:
            event: Событие для отправки

        Raises:
            ValueError: При ошибке сервера
        """
        response = await self._make_request(
            "POST",
            self.endpoints.setter_one,
            data=event,
            token=self.setter_token,
        )
        if response and "error" in response:
            raise ValueError(f"Server error: {response['error']}")

    async def setter_many(
        self, events: List[SetterEvent]
    ) -> Dict[int, str]:
        """
        Пакетная отправка событий

        Args:
            events: Список событий для отправки

        Returns:
            Словарь с ошибками по индексам событий
        """
        request_body = SetterRequestBody(events=events)
        response = await self._make_request(
            "POST",
            self.endpoints.setter_many,
            data=request_body,
            token=self.setter_token,
        )
        return SetterManyResponseBody(**response).errors

    async def setter_by_table(
        self, table_name: str, data: Dict[str, Any]
    ) -> None:
        """
        Отправка данных в конкретную таблицу

        Args:
            table_name: Имя таблицы
            data: Данные для отправки

        Raises:
            ValueError: При ошибке сервера
        """
        response = await self._make_request(
            "POST",
            self.endpoints.setter_by_table % table_name,
            data=data,
            token=self.setter_token,
        )
        if response and "error" in response:
            raise ValueError(f"Server error: {response['error']}") 


class ChClientBackground:
    """Клиент для работы с CH API в фоновом режиме"""

    def __init__(self, client: ChClient, error_callback: Optional[Callable[[BaseException], None]] = None):
        """
        Инициализация фонового клиента

        Args:
            client: Основной клиент CH API
            error_callback: Функция обратного вызова для обработки ошибок (по умолчанию логирует ошибки)
        """
        self.client = client
        self.error_callback = error_callback or self._default_error_handler
        
    def _default_error_handler(self, exc: BaseException) -> None:
        """Обработчик ошибок по умолчанию"""
        logging.warning("Ошибка в фоновой задаче: %s", exc)
        
    def _handle_background_task(self, task: asyncio.Task[T]) -> None:
        """Обработка ошибок фоновой задачи"""
        try:
            exc = task.exception()
            if exc:
                self.error_callback(exc)
        except asyncio.CancelledError:
            pass

    def setter_one(self, event: SetterEvent) -> asyncio.Task[None]:
        """Отправка одного события в фоновом режиме"""
        task = asyncio.create_task(self.client.setter_one(event))
        task.add_done_callback(self._handle_background_task)
        return task
    
    def setter_many(self, events: List[SetterEvent]) -> asyncio.Task[Dict[int, str]]:
        """Пакетная отправка событий в фоновом режиме"""
        task = asyncio.create_task(self.client.setter_many(events))
        task.add_done_callback(self._handle_background_task)
        return task
    
    def setter_by_table(self, table_name: str, data: Dict[str, Any]) -> asyncio.Task[None]:
        """Отправка данных в конкретную таблицу в фоновом режиме"""
        task = asyncio.create_task(self.client.setter_by_table(table_name, data))
        task.add_done_callback(self._handle_background_task)
        return task
    
    

    
    
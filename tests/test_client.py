"""
Тесты для клиента CH API
"""
import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from pychapi.client import ChClient
from pychapi.models import SetterEvent, ChEndpoints


@pytest.fixture
def client() -> ChClient:
    """Фикстура для создания клиента"""
    return ChClient(
        base_url="http://localhost:8080",
        setter_token="setter-token",
        getter_token="getter-token",
    )


@pytest.mark.asyncio
async def test_setter_one_success(client: ChClient) -> None:
    """Тест успешной отправки одного события"""
    event = SetterEvent(
        table_name="events",
        data={"field": "value"}
    )
    
    mock_response: Dict[str, Any] = {}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        await client.setter_one(event)
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_setter_one_error(client: ChClient) -> None:
    """Тест отправки одного события с ошибкой"""
    event = SetterEvent(
        table_name="events",
        data={"field": "value"}
    )
    
    mock_response: Dict[str, str] = {"error": "invalid data"}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 400
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        with pytest.raises(ValueError, match="Server error: invalid data"):
            await client.setter_one(event)
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_setter_many_success(client: ChClient) -> None:
    """Тест успешной пакетной отправки событий"""
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
    
    mock_response: Dict[str, Dict[int, str]] = {"errors": {}}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        errors = await client.setter_many(events)
        
        assert not errors
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_setter_many_with_errors(client: ChClient) -> None:
    """Тест пакетной отправки событий с ошибками"""
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
    
    mock_response: Dict[str, Dict[int, str]] = {"errors": {0: "invalid data"}}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        errors = await client.setter_many(events)
        
        assert errors == {0: "invalid data"}
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_setter_by_table_success(client: ChClient) -> None:
    """Тест успешной отправки данных в конкретную таблицу"""
    data: Dict[str, str] = {"field": "value"}
    
    mock_response: Dict[str, Any] = {}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        await client.setter_by_table("events", data)
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_setter_by_table_error(client: ChClient) -> None:
    """Тест отправки данных в конкретную таблицу с ошибкой"""
    data: Dict[str, str] = {"field": "value"}
    
    mock_response: Dict[str, str] = {"error": "invalid data"}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 400
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        with pytest.raises(ValueError, match="Server error: invalid data"):
            await client.setter_by_table("events", data)
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_custom_endpoints() -> None:
    """Тест использования пользовательских эндпоинтов"""
    endpoints = ChEndpoints(
        setter_many="/custom/many",
        setter_by_table="/custom/%s",
        setter_one="/custom/one"
    )
    
    client = ChClient(
        base_url="http://localhost:8080",
        setter_token="setter-token",
        getter_token="getter-token",
        endpoints=endpoints
    )
    
    event = SetterEvent(
        table_name="events",
        data={"field": "value"}
    )
    
    mock_response: Dict[str, Any] = {}
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_request.return_value.__aenter__.return_value = mock_response_obj
        
        await client.setter_one(event)
        
        mock_request.assert_called_once()
        call_args = mock_request.call_args[0]
        assert call_args[1] == "http://localhost:8080/custom/one" 
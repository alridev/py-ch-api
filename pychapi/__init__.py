"""
Асинхронная библиотека для работы с CH API
"""

from .client import ChClient
from .models import SetterEvent, ChEndpoints

__all__ = ["ChClient", "SetterEvent", "ChEndpoints"]

__version__ = "0.1.0" 
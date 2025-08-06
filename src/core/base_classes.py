"""
Abstract base classes for the application
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from telethon.tl.types import Message

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    async def calculate_amount(self, metadata: Dict[str, Any]) -> int:
        """Calculate trading amount based on metadata"""
        pass

class BaseMessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def process_message(self, message: Message, channel_title: str) -> None:
        """Process a message"""
        pass

class BaseOrderManager(ABC):
    """Abstract base class for order management"""
    
    @abstractmethod
    async def execute_buy_order(self, token_address: str, amount: int) -> Optional[Dict[str, Any]]:
        """Execute a buy order"""
        pass
    
    @abstractmethod
    async def execute_sell_order(self, token_address: str, amount: int) -> Optional[Dict[str, Any]]:
        """Execute a sell order"""
        pass 
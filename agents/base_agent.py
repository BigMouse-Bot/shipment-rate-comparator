"""Base agent for all carriers"""

from abc import ABC, abstractmethod
from typing import List, Optional
import asyncio
from tinyfish_client import TinyFishClient
from config import Config
from models import ShipmentPackage, ShippingRate, Carrier
from utils.logger import setup_logger

class BaseCarrierAgent(ABC):
    """Base class for carrier agents"""
    
    def __init__(self, carrier: Carrier):
        self.carrier = carrier
        self.logger = setup_logger(f"agent.{carrier.value.lower()}")
        self.client = TinyFishClient(api_key=Config.TINYFISH_API_KEY)
    
    @abstractmethod
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get shipping rates from carrier"""
        pass
    
    @abstractmethod
    async def get_rate_url(self) -> str:
        """Get URL for rate calculator"""
        pass
    
    @abstractmethod
    def get_form_selectors(self) -> dict:
        """Get CSS selectors for form fields"""
        pass
    
    async def close(self):
        """Close the client"""
        await self.client.close()

# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import List, Optional
import asyncio
from tinyfish import TinyFishClient, WebAgent
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
    
    async def _handle_cookie_consent(self, agent: WebAgent) -> None:
        """Handle cookie consent popups"""
        cookie_selectors = [
            "button[aria-label*='cookie']",
            "button[id*='cookie']",
            "#accept-cookies",
            ".cookie-accept",
            "button:contains('Accept')"
        ]
        
        for selector in cookie_selectors:
            try:
                if await agent.is_element_present(selector, timeout=2000):
                    await agent.click(selector)
                    self.logger.debug(f"Accepted cookies with selector: {selector}")
                    await asyncio.sleep(1)
                    break
            except Exception:
                continue
    
    async def _wait_for_results(self, agent: WebAgent, timeout: int = 15000) -> bool:
        """Wait for results table to load"""
        result_selectors = [
            "[data-testid='rate-results']",
            ".rate-results",
            ".shipping-rates",
            "[class*='rate'] table",
            ".rates-table"
        ]
        
        for selector in result_selectors:
            try:
                if await agent.wait_for_selector(selector, timeout=timeout):
                    self.logger.debug(f"Results found with selector: {selector}")
                    return True
            except Exception:
                continue
        
        return False
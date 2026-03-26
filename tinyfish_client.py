"""Custom TinyFish API client with Indian carrier support"""

import asyncio
import aiohttp
import json
import random
from typing import Optional, Dict, Any, List
from config import Config
from utils.logger import setup_logger

logger = setup_logger("tinyfish_client")

class TinyFishClient:
    """TinyFish API client for web automation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.TINYFISH_API_URL
        self.session = None
        self.mock_mode = True  # Set to True for development
        self.logger = logger
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session and not self.mock_mode:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
        return self.session
    
    async def create_agent(self, headless: bool = False, timeout: int = 30000) -> 'WebAgent':
        """Create a new web agent"""
        if self.mock_mode:
            logger.info("MOCK MODE: Creating Indian carrier agent")
            return WebAgent(f"indian_agent_{random.randint(1000, 9999)}", self)
        
        # Real API code would go here
        return WebAgent(f"agent_{random.randint(1000, 9999)}", self)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Client session closed")

class WebAgent:
    """Web agent for browser automation with Indian carrier support"""
    
    def __init__(self, agent_id: str, client: TinyFishClient):
        self.agent_id = agent_id
        self.client = client
        self.current_url = ""
        self.mock_mode = client.mock_mode
        self.logger = logger
        self.mock_data = {
            'dtdc': [
                {'service': 'DTDC Surface', 'price': 89, 'days': 5},
                {'service': 'DTDC Air', 'price': 149, 'days': 2},
                {'service': 'DTDC Express', 'price': 199, 'days': 1}
            ],
            'bluedart': [
                {'service': 'Blue Dart Surface', 'price': 129, 'days': 4},
                {'service': 'Blue Dart Air', 'price': 249, 'days': 2},
                {'service': 'Blue Dart Priority', 'price': 399, 'days': 1}
            ],
            'delhivery': [
                {'service': 'Delhivery Standard', 'price': 69, 'days': 5},
                {'service': 'Delhivery Express', 'price': 119, 'days': 3},
                {'service': 'Delhivery Priority', 'price': 179, 'days': 2}
            ],
            'indiapost': [
                {'service': 'India Post Speed Post', 'price': 49, 'days': 4},
                {'service': 'India Post Registered', 'price': 39, 'days': 6},
                {'service': 'India Post Express', 'price': 89, 'days': 3}
            ]
        }
    
    async def goto(self, url: str):
        """Navigate to URL"""
        self.current_url = url
        if self.mock_mode:
            self.logger.info(f"MOCK: Navigating to {url}")
            await asyncio.sleep(1)
    
    async def fill(self, selector: str, value: str):
        """Fill form field"""
        if self.mock_mode:
            self.logger.debug(f"MOCK: Filling {selector} with {value}")
            await asyncio.sleep(0.5)
    
    async def click(self, selector: str):
        """Click element"""
        if self.mock_mode:
            self.logger.debug(f"MOCK: Clicking {selector}")
            await asyncio.sleep(0.5)
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear"""
        if self.mock_mode:
            await asyncio.sleep(1)
            return True
        return True
    
    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript and return mock rates"""
        if self.mock_mode:
            await asyncio.sleep(1)
            
            # Return mock data based on URL
            if 'dtdc' in self.current_url.lower():
                return self.mock_data['dtdc']
            elif 'bluedart' in self.current_url.lower():
                return self.mock_data['bluedart']
            elif 'delhivery' in self.current_url.lower():
                return self.mock_data['delhivery']
            elif 'indiapost' in self.current_url.lower():
                return self.mock_data['indiapost']
            else:
                return [
                    {'service': 'Standard Shipping', 'price': 59, 'days': 4},
                    {'service': 'Express Shipping', 'price': 99, 'days': 2}
                ]
        return []
    
    async def is_element_present(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element exists"""
        if self.mock_mode:
            return True
        return True
    
    async def close(self):
        """Close the agent"""
        if self.mock_mode:
            self.logger.info(f"MOCK: Closing agent {self.agent_id}")

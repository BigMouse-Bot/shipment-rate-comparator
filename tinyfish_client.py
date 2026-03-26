"""TinyFish API client with mock fallback"""

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
        self.mock_mode = False
        self.logger = logger
        
        # Check if we're in mock mode
        if not api_key or api_key == 'your_api_key_here':
            self.mock_mode = True
            logger.warning("Running in MOCK MODE - No API key provided")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session and not self.mock_mode:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def create_agent(self, headless: bool = False, timeout: int = 30000) -> 'WebAgent':
        """Create a new web agent"""
        if self.mock_mode:
            logger.info("MOCK MODE: Creating mock agent")
            return WebAgent(f"mock_agent_{random.randint(1000, 9999)}", self)
        
        session = await self._get_session()
        
        try:
            response = await session.post(
                f"{self.base_url}/agents",
                json={
                    "headless": headless,
                    "timeout": timeout,
                    "user_agent": "Mozilla/5.0 (compatible; ShippingBot/1.0)"
                }
            )
            
            if response.status == 200:
                data = await response.json()
                agent_id = data.get('agent_id')
                logger.info(f"Created agent: {agent_id}")
                return WebAgent(agent_id, self)
            else:
                error_text = await response.text()
                logger.error(f"Failed to create agent: {error_text}")
                # Fallback to mock mode
                logger.warning("Falling back to MOCK MODE")
                self.mock_mode = True
                return WebAgent(f"mock_agent_{random.randint(1000, 9999)}", self)
                
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            # Fallback to mock mode
            logger.warning("Falling back to MOCK MODE")
            self.mock_mode = True
            return WebAgent(f"mock_agent_{random.randint(1000, 9999)}", self)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Client session closed")

class WebAgent:
    """Web agent for browser automation with mock support"""
    
    def __init__(self, agent_id: str, client: TinyFishClient):
        self.agent_id = agent_id
        self.client = client
        self.current_url = ""
        self.mock_mode = client.mock_mode
        self.logger = logger
        self.mock_data = {
            'fedex': [
                {'service': 'FedEx Ground', 'price': 12.99, 'days': 3},
                {'service': 'FedEx Express', 'price': 24.99, 'days': 1},
                {'service': 'FedEx 2Day', 'price': 18.99, 'days': 2}
            ],
            'ups': [
                {'service': 'UPS Ground', 'price': 11.99, 'days': 4},
                {'service': 'UPS Next Day Air', 'price': 29.99, 'days': 1},
                {'service': 'UPS 2nd Day Air', 'price': 19.99, 'days': 2}
            ],
            'usps': [
                {'service': 'USPS Ground Advantage', 'price': 9.99, 'days': 3},
                {'service': 'USPS Priority Mail', 'price': 15.99, 'days': 2},
                {'service': 'USPS Priority Express', 'price': 27.99, 'days': 1}
            ]
        }
    
    async def goto(self, url: str):
        """Navigate to URL"""
        self.current_url = url
        if self.mock_mode:
            self.logger.info(f"MOCK: Navigating to {url}")
            await asyncio.sleep(1)  # Simulate network delay
        else:
            session = await self.client._get_session()
            try:
                response = await session.post(
                    f"{self.client.base_url}/agents/{self.agent_id}/navigate",
                    json={"url": url}
                )
                if response.status == 200:
                    data = await response.json()
                    self.current_url = data.get('url', url)
                else:
                    raise Exception(f"Navigation failed: {response.status}")
            except Exception as e:
                self.logger.error(f"Error navigating: {str(e)}")
                raise
    
    async def fill(self, selector: str, value: str):
        """Fill form field"""
        if self.mock_mode:
            self.logger.debug(f"MOCK: Filling {selector} with {value}")
            await asyncio.sleep(0.5)
        else:
            session = await self.client._get_session()
            try:
                await session.post(
                    f"{self.client.base_url}/agents/{self.agent_id}/fill",
                    json={"selector": selector, "value": value}
                )
            except Exception as e:
                self.logger.error(f"Error filling: {str(e)}")
    
    async def click(self, selector: str):
        """Click element"""
        if self.mock_mode:
            self.logger.debug(f"MOCK: Clicking {selector}")
            await asyncio.sleep(0.5)
        else:
            session = await self.client._get_session()
            try:
                await session.post(
                    f"{self.client.base_url}/agents/{self.agent_id}/click",
                    json={"selector": selector}
                )
            except Exception as e:
                self.logger.error(f"Error clicking: {str(e)}")
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear"""
        if self.mock_mode:
            self.logger.debug(f"MOCK: Waiting for {selector}")
            await asyncio.sleep(1)
            return True
        else:
            session = await self.client._get_session()
            try:
                response = await session.post(
                    f"{self.client.base_url}/agents/{self.agent_id}/wait",
                    json={"selector": selector, "timeout": timeout}
                )
                return response.status == 200
            except:
                return False
    
    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript and return mock rates"""
        if self.mock_mode:
            # Return mock data based on URL
            self.logger.debug(f"MOCK: Evaluating script")
            await asyncio.sleep(1)
            
            # Return mock rates based on carrier in URL
            if 'fedex' in self.current_url.lower():
                return self.mock_data['fedex']
            elif 'ups' in self.current_url.lower():
                return self.mock_data['ups']
            elif 'usps' in self.current_url.lower():
                return self.mock_data['usps']
            else:
                # Return generic rates
                return [
                    {'service': 'Ground Shipping', 'price': 10.99, 'days': 3},
                    {'service': 'Express Shipping', 'price': 22.99, 'days': 1}
                ]
        else:
            session = await self.client._get_session()
            try:
                response = await session.post(
                    f"{self.client.base_url}/agents/{self.agent_id}/evaluate",
                    json={"script": script}
                )
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', [])
                else:
                    return []
            except:
                return []
    
    async def is_element_present(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element exists"""
        if self.mock_mode:
            return True
        try:
            return await self.wait_for_selector(selector, timeout)
        except:
            return False
    
    async def close(self):
        """Close the agent"""
        if self.mock_mode:
            self.logger.info(f"MOCK: Closing agent {self.agent_id}")
        else:
            session = await self.client._get_session()
            try:
                await session.delete(
                    f"{self.client.base_url}/agents/{self.agent_id}"
                )
            except:
                pass

"""India Post rate calculator agent"""

import asyncio
from typing import List
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class IndiaPostAgent(BaseCarrierAgent):
    """India Post rate calculator agent"""
    
    def __init__(self):
        super().__init__(Carrier.INDIA_POST)
    
    async def get_rate_url(self) -> str:
        return "https://www.indiapost.gov.in/Financial/Pages/Content/Postal-Rates.aspx"
    
    def get_form_selectors(self) -> dict:
        return {
            'weight': "input[name='weight']",
            'origin': "input[name='origin']",
            'destination': "input[name='destination']",
            'submit': "button[type='submit']"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from India Post"""
        rates = []
        agent = None
        
        try:
            agent = await self.client.create_agent(
                headless=Config.HEADLESS_MODE,
                timeout=Config.TIMEOUT_SECONDS * 1000
            )
            
            self.logger.info(f"Getting rates from India Post...")
            await agent.goto(await self.get_rate_url())
            await asyncio.sleep(2)
            
            await self._handle_cookie_consent(agent)
            
            # Fill form
            await agent.fill("input[name='weight']", str(package.weight_kg))
            await agent.fill("input[name='origin']", package.origin_pincode)
            await agent.fill("input[name='destination']", package.destination_pincode)
            
            await agent.click("button[type='submit']")
            await asyncio.sleep(3)
            
            # Mock data for India Post (cheapest but slowest)
            mock_rates = [
                {'service': 'India Post Speed Post', 'price': 49, 'days': 4},
                {'service': 'India Post Registered', 'price': 39, 'days': 6},
                {'service': 'India Post Express', 'price': 89, 'days': 3}
            ]
            
            for rate_data in mock_rates:
                rate = ShippingRate(
                    carrier=self.carrier,
                    service_name=rate_data['service'],
                    service_level=ServiceLevel.ECONOMY,
                    price_inr=rate_data['price'],
                    delivery_days=rate_data['days'],
                    tracking_included=True,
                    url=agent.current_url
                )
                rates.append(rate)
                self.logger.info(f"  {rate.service_name}: {rate.formatted_price} ({rate.delivery_days} days)")
            
        except Exception as e:
            self.logger.error(f"India Post error: {str(e)}")
            
        finally:
            if agent:
                await agent.close()
        
        return rates

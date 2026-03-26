"""Delhivery rate calculator agent - Indian carrier"""

import asyncio
from typing import List
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class DelhiveryAgent(BaseCarrierAgent):
    """Delhivery rate calculator agent"""
    
    def __init__(self):
        super().__init__(Carrier.DELHIVERY)
    
    async def get_rate_url(self) -> str:
        return "https://www.delhivery.com/shipping/rate-calculator"
    
    def get_form_selectors(self) -> dict:
        return {
            'weight': "input[name='weight']",
            'origin': "input[name='originPincode']",
            'destination': "input[name='destPincode']",
            'submit': "button[type='submit']"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from Delhivery"""
        rates = []
        agent = None
        
        try:
            agent = await self.client.create_agent(
                headless=Config.HEADLESS_MODE,
                timeout=Config.TIMEOUT_SECONDS * 1000
            )
            
            self.logger.info(f"Getting rates from Delhivery...")
            await agent.goto(await self.get_rate_url())
            await asyncio.sleep(2)
            
            await self._handle_cookie_consent(agent)
            
            # Fill form
            await agent.fill("input[name='weight']", str(package.weight_kg))
            await agent.fill("input[name='origin']", package.origin_pincode)
            await agent.fill("input[name='destination']", package.destination_pincode)
            
            await agent.click("button[type='submit']")
            await asyncio.sleep(3)
            
            # Mock data for Delhivery (budget friendly)
            mock_rates = [
                {'service': 'Delhivery Standard', 'price': 69, 'days': 5},
                {'service': 'Delhivery Express', 'price': 119, 'days': 3},
                {'service': 'Delhivery Priority', 'price': 179, 'days': 2}
            ]
            
            for rate_data in mock_rates:
                rate = ShippingRate(
                    carrier=self.carrier,
                    service_name=rate_data['service'],
                    service_level=ServiceLevel.STANDARD,
                    price_inr=rate_data['price'],
                    delivery_days=rate_data['days'],
                    tracking_included=True,
                    url=agent.current_url
                )
                rates.append(rate)
                self.logger.info(f"  {rate.service_name}: {rate.formatted_price} ({rate.delivery_days} days)")
            
        except Exception as e:
            self.logger.error(f"Delhivery error: {str(e)}")
            
        finally:
            if agent:
                await agent.close()
        
        return rates

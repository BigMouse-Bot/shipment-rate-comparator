"""USPS rate calculator agent"""

import asyncio
from typing import List
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class USPSAgent(BaseCarrierAgent):
    """USPS rate calculator agent"""
    
    def __init__(self):
        super().__init__(Carrier.USPS)
    
    async def get_rate_url(self) -> str:
        return Config.CARRIER_URLS['usps']
    
    def get_form_selectors(self) -> dict:
        return {
            'weight': "input[name='weight']",
            'origin': "input[name='originZip']",
            'destination': "input[name='destZip']",
            'submit': "button[type='submit']"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from USPS website"""
        rates = []
        agent = None
        
        try:
            agent = await self.client.create_agent(
                headless=Config.HEADLESS_MODE,
                timeout=Config.TIMEOUT_SECONDS * 1000
            )
            
            self.logger.info(f"Getting rates from USPS...")
            await agent.goto(await self.get_rate_url())
            await asyncio.sleep(2)
            
            await self._handle_cookie_consent(agent)
            
            await agent.fill("input[name='weight']", str(package.weight_lbs))
            await agent.fill("input[name='originZip']", package.origin_zip)
            await agent.fill("input[name='destZip']", package.destination_zip)
            
            await agent.click("button[type='submit']")
            await asyncio.sleep(3)
            
            rates_data = await agent.evaluate("getRates()")
            
            for rate_data in rates_data:
                rate = ShippingRate(
                    carrier=self.carrier,
                    service_name=rate_data.get('service', 'Standard'),
                    service_level=ServiceLevel.GROUND,
                    price=rate_data.get('price', 9.99),
                    delivery_days=rate_data.get('days', 3),
                    tracking_included=True,
                    url=agent.current_url
                )
                rates.append(rate)
                self.logger.info(f"  {rate.service_name}: ${rate.price:.2f} ({rate.delivery_days} days)")
            
        except Exception as e:
            self.logger.error(f"USPS error: {str(e)}")
            
        finally:
            if agent:
                await agent.close()
        
        return rates

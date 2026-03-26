"""Blue Dart rate calculator agent - Indian carrier"""

import asyncio
from typing import List
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class BlueDartAgent(BaseCarrierAgent):
    """Blue Dart rate calculator agent"""
    
    def __init__(self):
        super().__init__(Carrier.BLUEDART)
    
    async def get_rate_url(self) -> str:
        return "https://www.bluedart.com/shipping/rate-calculator"
    
    def get_form_selectors(self) -> dict:
        return {
            'weight': "input[name='weight']",
            'origin': "input[name='originPincode']",
            'destination': "input[name='destPincode']",
            'submit': "button[type='submit']"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from Blue Dart"""
        rates = []
        agent = None
        
        try:
            agent = await self.client.create_agent(
                headless=Config.HEADLESS_MODE,
                timeout=Config.TIMEOUT_SECONDS * 1000
            )
            
            self.logger.info(f"Getting rates from Blue Dart...")
            await agent.goto(await self.get_rate_url())
            await asyncio.sleep(2)
            
            await self._handle_cookie_consent(agent)
            
            # Fill form
            await agent.fill("input[name='weight']", str(package.weight_kg))
            await agent.fill("input[name='origin']", package.origin_pincode)
            await agent.fill("input[name='destination']", package.destination_pincode)
            
            await agent.click("button[type='submit']")
            await asyncio.sleep(3)
            
            # Mock data for Blue Dart (premium pricing)
            mock_rates = [
                {'service': 'Blue Dart Surface', 'price': 129, 'days': 4},
                {'service': 'Blue Dart Air', 'price': 249, 'days': 2},
                {'service': 'Blue Dart Priority', 'price': 399, 'days': 1}
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
            self.logger.error(f"Blue Dart error: {str(e)}")
            
        finally:
            if agent:
                await agent.close()
        
        return rates

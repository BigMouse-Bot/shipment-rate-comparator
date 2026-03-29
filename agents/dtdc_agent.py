"""DTDC Rate Agent - Using Real TinyFish API"""

import asyncio
from typing import List
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class DTDCAgent(BaseCarrierAgent):
    """DTDC rate calculator agent - REAL API"""
    
    def __init__(self):
        super().__init__(Carrier.DTDC)
    
    async def get_rate_url(self) -> str:
        return "https://www.dtdc.in"
    
    def get_form_selectors(self) -> dict:
        return {}
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get REAL rates from DTDC using TinyFish API"""
        rates = []
        
        try:
            self.logger.info(f"Getting REAL rates from DTDC for {package.weight_kg}kg...")
            
            # Call the real API
            result = await self.client.get_shipping_rates(
                package.weight_kg, 
                package.origin_pincode, 
                package.destination_pincode
            )
            
            if "error" in result:
                self.logger.error(f"API error: {result['error']}")
                return []
            
            # Parse the real rates
            rate_slabs = result.get('rates', [])
            
            for slab in rate_slabs:
                weight_range = slab.get('weight_slab', '')
                
                # Extract prices for different services
                if 'DTDC Lite' in slab:
                    price_str = slab['DTDC Lite']
                    # Parse price range (e.g., "₹40 – ₹100" -> take average)
                    price = self._parse_price(price_str)
                    if price > 0:
                        rates.append(ShippingRate(
                            carrier=self.carrier,
                            service_name="DTDC Lite",
                            service_level=ServiceLevel.ECONOMY,
                            price_inr=price,
                            delivery_days=5,
                            tracking_included=True,
                            url=await self.get_rate_url()
                        ))
                
                if 'DTDC Plus' in slab:
                    price_str = slab['DTDC Plus']
                    price = self._parse_price(price_str)
                    if price > 0:
                        rates.append(ShippingRate(
                            carrier=self.carrier,
                            service_name="DTDC Plus",
                            service_level=ServiceLevel.STANDARD,
                            price_inr=price,
                            delivery_days=3,
                            tracking_included=True,
                            url=await self.get_rate_url()
                        ))
                
                if 'DTDC Prime' in slab:
                    price_str = slab['DTDC Prime']
                    price = self._parse_price(price_str)
                    if price > 0:
                        rates.append(ShippingRate(
                            carrier=self.carrier,
                            service_name="DTDC Prime",
                            service_level=ServiceLevel.EXPRESS,
                            price_inr=price,
                            delivery_days=2,
                            tracking_included=True,
                            url=await self.get_rate_url()
                        ))
            
            self.logger.info(f"Found {len(rates)} REAL rates from DTDC")
            
        except Exception as e:
            self.logger.error(f"DTDC error: {str(e)}")
        
        return rates
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string like '₹40 – ₹100' or '₹40' to float"""
        import re
        # Extract numbers
        numbers = re.findall(r'(\d+)', price_str)
        if numbers:
            # If range, take average
            prices = [int(n) for n in numbers]
            return sum(prices) / len(prices)
        return 0

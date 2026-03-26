import asyncio
from tinyfish import TinyFishClient
from typing import List
from .fedex import ShippingRate  # Reuse the same dataclass

class UPSRateAgent:
    def __init__(self, api_key: str):
        self.client = TinyFishClient(api_key=api_key)
    
    async def get_rates(self, package) -> List[ShippingRate]:
        """Get shipping rates from UPS"""
        agent = await self.client.create_agent(headless=False)
        
        try:
            # UPS rate calculator
            await agent.goto("https://www.ups.com/ship/guided/choose-services")
            await asyncio.sleep(3)
            
            # Fill out the form
            await agent.fill_form({
                "input[name='originPostalCode']": package.origin_zip,
                "input[name='destPostalCode']": package.destination_zip,
                "input[name='weight']": str(package.weight_lbs),
                "input[name='length']": str(package.length_in),
                "input[name='width']": str(package.width_in),
                "input[name='height']": str(package.height_in)
            })
            
            # Submit
            await agent.click("button[type='submit']")
            await asyncio.sleep(5)
            
            # Extract rates
            rates_data = await agent.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('.rate-item').forEach(item => {
                        results.push({
                            service: item.querySelector('.service-type')?.innerText || '',
                            price: item.querySelector('.total-charges')?.innerText || '$0',
                            delivery: item.querySelector('.delivery-time')?.innerText || ''
                        });
                    });
                    return results;
                }
            """)
            
            shipping_rates = []
            for rate in rates_data:
                price = float(rate['price'].replace('$', '').replace(',', ''))
                shipping_rates.append(ShippingRate(
                    carrier="UPS",
                    service_name=rate['service'],
                    price=price,
                    delivery_days=rate['delivery'],
                    estimated_delivery_date=None,
                    tracking_included=True,
                    url=agent.current_url
                ))
            
            return shipping_rates
            
        finally:
            await agent.close()
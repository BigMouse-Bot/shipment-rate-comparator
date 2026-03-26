import asyncio
from tinyfish import TinyFishClient
from dataclasses import dataclass
from typing import List, Optional
import os

@dataclass
class ShippingRate:
    carrier: str
    service_name: str
    price: float
    delivery_days: str
    estimated_delivery_date: Optional[str]
    tracking_included: bool
    url: str

class FedExRateAgent:
    def __init__(self, api_key: str):
        self.client = TinyFishClient(api_key=api_key)
    
    async def get_rates(self, package) -> List[ShippingRate]:
        """Get shipping rates from FedEx"""
        agent = await self.client.create_agent(
            headless=False,  # Set to True in production
            timeout=30000,
            user_agent="Mozilla/5.0 (compatible; ShippingBot/1.0)"
        )
        
        try:
            # Navigate to FedEx rate calculator
            await agent.goto("https://www.fedex.com/en-us/shipping/shipping-rates.html")
            await asyncio.sleep(3)  # Wait for page load
            
            # Handle cookie consent if present
            try:
                await agent.click("button[aria-label='Accept Cookies']", timeout=3000)
            except:
                pass
            
            # Fill out the form
            await agent.fill_form({
                "input[name='packageWeight']": str(package.weight_lbs),
                "input[name='packageLength']": str(package.length_in),
                "input[name='packageWidth']": str(package.width_in),
                "input[name='packageHeight']": str(package.height_in),
                "input[name='originPostalCode']": package.origin_zip,
                "input[name='destinationPostalCode']": package.destination_zip
            })
            
            # Submit form
            await agent.click("button[type='submit']")
            await asyncio.sleep(5)  # Wait for results
            
            # Extract rates using TinyFish's built-in extraction
            rates_data = await agent.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('.rate-row').forEach(row => {
                        const service = row.querySelector('.service-name')?.innerText || '';
                        const priceText = row.querySelector('.price-amount')?.innerText || '$0';
                        const delivery = row.querySelector('.delivery-days')?.innerText || '';
                        const date = row.querySelector('.delivery-date')?.innerText || '';
                        
                        // Parse price (remove $ and convert to float)
                        const price = parseFloat(priceText.replace('$', '').replace(',', ''));
                        
                        results.push({
                            service: service,
                            price: price,
                            delivery: delivery,
                            date: date
                        });
                    });
                    return results;
                }
            """)
            
            # Convert to ShippingRate objects
            shipping_rates = []
            for rate in rates_data:
                shipping_rates.append(ShippingRate(
                    carrier="FedEx",
                    service_name=rate['service'],
                    price=rate['price'],
                    delivery_days=rate['delivery'],
                    estimated_delivery_date=rate['date'],
                    tracking_included=True,
                    url=agent.current_url
                ))
            
            return shipping_rates
            
        finally:
            await agent.close()
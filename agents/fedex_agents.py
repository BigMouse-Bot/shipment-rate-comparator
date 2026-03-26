# agents/fedex_agent.py
import asyncio
from typing import List
from tinyfish import WebAgent
from agents.base_agent import BaseCarrierAgent
from models import ShipmentPackage, ShippingRate, Carrier, ServiceLevel
from config import Config

class FedExAgent(BaseCarrierAgent):
    """FedEx rate calculator agent"""
    
    def __init__(self):
        super().__init__(Carrier.FEDEX)
    
    async def get_rate_url(self) -> str:
        return Config.CARRIER_URLS['fedex']
    
    def get_form_selectors(self) -> dict:
        """FedEx-specific CSS selectors"""
        return {
            'weight': "input[name='packageWeight'], input[id='packageWeight'], [data-testid='weight-input']",
            'length': "input[name='packageLength'], input[id='packageLength']",
            'width': "input[name='packageWidth'], input[id='packageWidth']",
            'height': "input[name='packageHeight'], input[id='packageHeight']",
            'origin': "input[name='originPostalCode'], input[id='originPostalCode']",
            'destination': "input[name='destinationPostalCode'], input[id='destinationPostalCode']",
            'submit': "button[type='submit'], button:contains('Get Rate'), button:contains('Calculate')",
            'declared_value': "input[name='declaredValue'], input[id='declaredValue']"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from FedEx website"""
        rates = []
        retries = 0
        
        while retries < Config.MAX_RETRIES:
            agent = None
            try:
                agent = await self.client.create_agent(
                    headless=Config.HEADLESS_MODE,
                    timeout=Config.TIMEOUT_SECONDS * 1000
                )
                
                # Navigate to rate calculator
                self.logger.info(f"Navigating to FedEx rate calculator...")
                await agent.goto(await self.get_rate_url())
                await asyncio.sleep(2)
                
                # Handle cookie consent
                await self._handle_cookie_consent(agent)
                
                # Wait for form to load
                selectors = self.get_form_selectors()
                await agent.wait_for_selector(selectors['weight'], timeout=10000)
                
                # Fill out the form
                self.logger.info(f"Filling shipment details for {package.origin_zip} -> {package.destination_zip}")
                
                await agent.fill(selectors['weight'], str(package.weight_lbs))
                await agent.fill(selectors['length'], str(package.length_in))
                await agent.fill(selectors['width'], str(package.width_in))
                await agent.fill(selectors['height'], str(package.height_in))
                await agent.fill(selectors['origin'], package.origin_zip)
                await agent.fill(selectors['destination'], package.destination_zip)
                
                # Fill declared value if provided
                if package.declared_value and selectors.get('declared_value'):
                    await agent.fill(selectors['declared_value'], str(package.declared_value))
                
                # Submit form
                self.logger.info("Submitting form...")
                await agent.click(selectors['submit'])
                
                # Wait for results
                results_found = await self._wait_for_results(agent)
                
                if results_found:
                    # Extract rates from page
                    rates_data = await agent.evaluate("""
                        () => {
                            const rates = [];
                            const rateRows = document.querySelectorAll('[class*="rate-row"], [class*="service-row"], tr[class*="rate"]');
                            
                            rateRows.forEach(row => {
                                const serviceElem = row.querySelector('[class*="service"], [class*="service-name"]');
                                const priceElem = row.querySelector('[class*="price"], [class*="rate"]');
                                const daysElem = row.querySelector('[class*="days"], [class*="delivery"]');
                                
                                if (serviceElem && priceElem) {
                                    let priceText = priceElem.innerText;
                                    let priceMatch = priceText.match(/\\$?(\\d+(?:\\.\\d{2})?)/);
                                    let price = priceMatch ? parseFloat(priceMatch[1]) : 0;
                                    
                                    let daysText = daysElem ? daysElem.innerText : "";
                                    let daysMatch = daysText.match(/(\\d+)/);
                                    let days = daysMatch ? parseInt(daysMatch[1]) : 3;
                                    
                                    rates.push({
                                        service: serviceElem.innerText.trim(),
                                        price: price,
                                        delivery_days: days
                                    });
                                }
                            });
                            
                            return rates;
                        }
                    """)
                    
                    # Convert to ShippingRate objects
                    for rate_data in rates_data:
                        if rate_data['price'] > 0:
                            service_level = self._get_service_level(rate_data['service'])
                            rate = ShippingRate(
                                carrier=self.carrier,
                                service_name=rate_data['service'],
                                service_level=service_level,
                                price=rate_data['price'],
                                delivery_days=rate_data['delivery_days'],
                                tracking_included=True,
                                url=agent.current_url
                            )
                            rates.append(rate)
                            self.logger.debug(f"Found rate: {rate.service_name} - ${rate.price:.2f}")
                    
                    if rates:
                        self.logger.info(f"Successfully retrieved {len(rates)} rates from FedEx")
                        break
                    else:
                        self.logger.warning("No rates found on page")
                        
            except Exception as e:
                retries += 1
                self.logger.error(f"FedEx agent error (attempt {retries}/{Config.MAX_RETRIES}): {str(e)}")
                if retries >= Config.MAX_RETRIES:
                    self.logger.error("Max retries reached for FedEx")
                    
            finally:
                if agent:
                    await agent.close()
                    await asyncio.sleep(1)
        
        return rates
    
    def _get_service_level(self, service_name: str) -> ServiceLevel:
        """Map FedEx service name to ServiceLevel enum"""
        service_lower = service_name.lower()
        
        if 'same day' in service_lower:
            return ServiceLevel.SAME_DAY
        elif 'overnight' in service_lower or 'first' in service_lower:
            return ServiceLevel.NEXT_DAY
        elif '2day' in service_lower or '2 day' in service_lower:
            return ServiceLevel.TWO_DAY
        elif 'express saver' in service_lower or '3day' in service_lower:
            return ServiceLevel.THREE_DAY
        elif 'ground' in service_lower:
            return ServiceLevel.GROUND
        else:
            return ServiceLevel.ECONOMY
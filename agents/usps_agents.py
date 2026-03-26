# agents/usps_agent.py
import asyncio
from typing import List
from tinyfish import WebAgent
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
        """USPS-specific CSS selectors"""
        return {
            'weight': "input[name='weight'], #weight, [data-testid='weight']",
            'origin': "input[name='originZip'], #originZip",
            'destination': "input[name='destZip'], #destZip",
            'submit': "button[type='submit'], input[type='submit'], .calc-button",
            'shape': "select[name='shape'], #shape"
        }
    
    async def get_rates(self, package: ShipmentPackage) -> List[ShippingRate]:
        """Get rates from USPS website"""
        rates = []
        retries = 0
        
        while retries < Config.MAX_RETRIES:
            agent = None
            try:
                agent = await self.client.create_agent(
                    headless=Config.HEADLESS_MODE,
                    timeout=Config.TIMEOUT_SECONDS * 1000
                )
                
                self.logger.info(f"Navigating to USPS rate calculator...")
                await agent.goto(await self.get_rate_url())
                await asyncio.sleep(2)
                
                await self._handle_cookie_consent(agent)
                
                selectors = self.get_form_selectors()
                await agent.wait_for_selector(selectors['weight'], timeout=10000)
                
                self.logger.info(f"Filling shipment details...")
                await agent.fill(selectors['weight'], str(package.weight_lbs))
                await agent.fill(selectors['origin'], package.origin_zip)
                await agent.fill(selectors['destination'], package.destination_zip)
                
                # Set shape to rectangular package
                if selectors.get('shape'):
                    try:
                        await agent.select(selectors['shape'], 'package')
                    except:
                        pass
                
                self.logger.info("Submitting for rates...")
                await agent.click(selectors['submit'])
                
                results_found = await self._wait_for_results(agent)
                
                if results_found:
                    rates_data = await agent.evaluate("""
                        () => {
                            const rates = [];
                            const rateRows = document.querySelectorAll('[class*="mail-class"], .rate-row, tr');
                            
                            rateRows.forEach(row => {
                                const serviceElem = row.querySelector('[class*="service"], .mail-class-name');
                                const priceElem = row.querySelector('[class*="price"], .rate');
                                
                                if (serviceElem && priceElem && serviceElem.innerText.trim()) {
                                    let priceText = priceElem.innerText;
                                    let priceMatch = priceText.match(/\\$?(\\d+(?:\\.\\d{2})?)/);
                                    let price = priceMatch ? parseFloat(priceMatch[1]) : 0;
                                    
                                    if (price > 0) {
                                        rates.push({
                                            service: serviceElem.innerText.trim(),
                                            price: price,
                                            delivery_days: 3
                                        });
                                    }
                                }
                            });
                            
                            return rates;
                        }
                    """)
                    
                    for rate_data in rates_data:
                        rate = ShippingRate(
                            carrier=self.carrier,
                            service_name=rate_data['service'],
                            service_level=self._get_service_level(rate_data['service']),
                            price=rate_data['price'],
                            delivery_days=rate_data.get('delivery_days', 3),
                            tracking_included=True,
                            url=agent.current_url
                        )
                        rates.append(rate)
                    
                    if rates:
                        self.logger.info(f"Successfully retrieved {len(rates)} rates from USPS")
                        break
                        
            except Exception as e:
                retries += 1
                self.logger.error(f"USPS agent error (attempt {retries}/{Config.MAX_RETRIES}): {str(e)}")
                
            finally:
                if agent:
                    await agent.close()
                    await asyncio.sleep(1)
        
        return rates
    
    def _get_service_level(self, service_name: str) -> ServiceLevel:
        """Map USPS service name to ServiceLevel enum"""
        service_lower = service_name.lower()
        
        if 'priority mail express' in service_lower:
            return ServiceLevel.NEXT_DAY
        elif 'priority mail' in service_lower:
            return ServiceLevel.TWO_DAY
        elif 'ground advantage' in service_lower:
            return ServiceLevel.GROUND
        else:
            return ServiceLevel.ECONOMY
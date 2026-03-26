"""Orchestrator for rate comparison"""

import asyncio
from typing import List, Dict, Optional
from models import ShipmentPackage, ShippingRate, ComparisonResult, Carrier
from agents import FedExAgent, UPSAgent, USPSAgent
from utils.logger import setup_logger

class ShippingRateOrchestrator:
    """Orchestrates rate comparison across multiple carriers"""
    
    def __init__(self):
        self.logger = setup_logger("orchestrator")
        self.agents = {
            Carrier.FEDEX: FedExAgent(),
            Carrier.UPS: UPSAgent(),
            Carrier.USPS: USPSAgent()
        }
    
    async def compare_rates(
        self, 
        package: ShipmentPackage, 
        carriers: Optional[List[Carrier]] = None
    ) -> ComparisonResult:
        """Compare rates across specified carriers"""
        
        self.logger.info(f"Starting rate comparison for {package.origin_zip} -> {package.destination_zip}")
        
        # Determine which carriers to query
        target_carriers = carriers or list(self.agents.keys())
        
        # Run all agents in parallel
        tasks = []
        for carrier in target_carriers:
            if carrier in self.agents:
                agent = self.agents[carrier]
                tasks.append(agent.get_rates(package))
                self.logger.debug(f"Scheduled {carrier.value} agent")
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all rates
        all_rates = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Agent failed: {str(result)}")
            elif isinstance(result, list):
                all_rates.extend(result)
        
        self.logger.info(f"Collected {len(all_rates)} rates total")
        
        return ComparisonResult(
            package=package,
            rates=all_rates
        )
    
    def find_best_rates(self, result: ComparisonResult) -> Dict:
        """Find best rate options from comparison result"""
        if not result.rates:
            return {
                'cheapest': None,
                'fastest': None,
                'best_value': None,
                'all_quotes': []
            }
        
        cheapest = min(result.rates, key=lambda x: x.price)
        fastest = min(result.rates, key=lambda x: x.delivery_days)
        
        # Calculate best value (price per day)
        best_value = min(result.rates, key=lambda x: x.price / max(x.delivery_days, 1))
        
        # Prepare all quotes for display
        all_quotes = []
        for rate in sorted(result.rates, key=lambda x: x.price):
            all_quotes.append({
                'carrier': rate.carrier.value,
                'service': rate.service_name,
                'price': rate.price,
                'delivery_days': rate.delivery_days,
                'price_per_day': rate.price / max(rate.delivery_days, 1)
            })
        
        return {
            'cheapest': {
                'carrier': cheapest.carrier.value,
                'service': cheapest.service_name,
                'price': cheapest.price,
                'delivery_days': cheapest.delivery_days
            },
            'fastest': {
                'carrier': fastest.carrier.value,
                'service': fastest.service_name,
                'price': fastest.price,
                'delivery_days': fastest.delivery_days
            },
            'best_value': {
                'carrier': best_value.carrier.value,
                'service': best_value.service_name,
                'price': best_value.price,
                'delivery_days': best_value.delivery_days,
                'value_score': best_value.price / max(best_value.delivery_days, 1)
            },
            'all_quotes': all_quotes
        }

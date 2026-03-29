#!/usr/bin/env python3
"""
Orchestrator for comparing rates across carriers
"""

import logging
from typing import Dict, List, Optional
from tinyfish_client import TinyFishClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateOrchestrator:
    def __init__(self, api_key: str):
        self.client = TinyFishClient(api_key)
        
    def compare_rates(self, weight_kg: float, origin: str, dest: str) -> List[Dict]:
        """Compare rates across all carriers"""
        
        results = []
        
        # DTDC
        logger.info(f"Getting REAL rates from DTDC for {weight_kg}kg...")
        dtdc_result = self.client.get_dtdc_rates(weight_kg, origin, dest)
        if dtdc_result:
            # Extract primary service
            if "primary_service" in dtdc_result:
                primary = dtdc_result["primary_service"]
                results.append({
                    "carrier": "DTDC",
                    "service": primary.get("service", "Standard"),
                    "price": primary.get("estimated_price"),
                    "price_display": f"₹{primary.get('estimated_price', 0):,.2f}",
                    "delivery_time": primary.get("delivery_time", "3-5 days"),
                    "weight_kg": weight_kg,
                    "all_options": dtdc_result.get("additional_options", [])
                })
            else:
                # Fallback: try to extract price from any field
                price = self._extract_price(dtdc_result)
                results.append({
                    "carrier": "DTDC",
                    "service": "Standard",
                    "price": price,
                    "price_display": f"₹{price:,.2f}" if price else "N/A",
                    "delivery_time": "3-5 days",
                    "weight_kg": weight_kg
                })
            logger.info(f"✅ DTDC: ₹{results[-1]['price']:,.2f}" if results[-1].get('price') else "⚠️ DTDC: No price")
        else:
            results.append({"carrier": "DTDC", "error": "No response", "price": None})
        
        # Other carriers (you can implement these similarly)
        other_carriers = [
            ("Blue Dart", None, "Premium", "3-4 days"),
            ("Delhivery", None, "Express", "3-5 days"),
            ("India Post", None, "Speed Post", "5-7 days"),
        ]
        
        for name, price, service, delivery in other_carriers:
            results.append({
                "carrier": name,
                "service": service,
                "price": price,
                "price_display": "Coming soon",
                "delivery_time": delivery,
                "weight_kg": weight_kg,
                "note": "Integration in progress"
            })
        
        return results
    
    def _extract_price(self, data: Dict, max_depth: int = 3) -> Optional[float]:
        """Recursively extract price from JSON response"""
        if max_depth < 0:
            return None
            
        if isinstance(data, dict):
            # Check common price fields
            for key in ['estimated_price', 'price', 'rate', 'cost', 'amount']:
                if key in data:
                    val = data[key]
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str) and val.replace('.', '').isdigit():
                        return float(val)
            
            # Search nested
            for value in data.values():
                result = self._extract_price(value, max_depth - 1)
                if result is not None:
                    return result
                    
        elif isinstance(data, list):
            for item in data:
                result = self._extract_price(item, max_depth - 1)
                if result is not None:
                    return result
                    
        return None

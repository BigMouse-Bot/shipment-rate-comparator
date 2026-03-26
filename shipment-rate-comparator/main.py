import os
import asyncio
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
from tabulate import tabulate

# Import carrier agents
from carriers.fedex import FedExRateAgent, ShippingRate
from carriers.ups import UPSRateAgent

load_dotenv()

@dataclass
class ShipmentPackage:
    """Represents a package to be shipped"""
    weight_lbs: float
    length_in: float
    width_in: float
    height_in: float
    origin_zip: str
    destination_zip: str
    declared_value: Optional[float] = None

class ShippingRateOrchestrator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.carriers = {
            'fedex': FedExRateAgent(api_key),
            'ups': UPSRateAgent(api_key),
            # Add more carriers here
        }
    
    async def compare_rates(self, package: ShipmentPackage, 
                           carriers: Optional[List[str]] = None) -> Dict[str, List[ShippingRate]]:
        """Compare rates across multiple carriers in parallel"""
        target_carriers = carriers if carriers else list(self.carriers.keys())
        
        # Create tasks for each carrier
        tasks = []
        for carrier_name in target_carriers:
            if carrier_name in self.carriers:
                agent = self.carriers[carrier_name]
                tasks.append(self._get_rates_with_timeout(agent, package, carrier_name))
        
        # Run all carriers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_rates = {}
        for carrier_name, result in zip(target_carriers, results):
            if isinstance(result, Exception):
                print(f"⚠️ Error with {carrier_name}: {result}")
                all_rates[carrier_name] = []
            else:
                all_rates[carrier_name] = result
        
        return all_rates
    
    async def _get_rates_with_timeout(self, agent, package, carrier_name, timeout=30):
        """Wrapper with timeout for each carrier"""
        try:
            return await asyncio.wait_for(
                agent.get_rates(package), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"⏱️ {carrier_name} timed out")
            return []
    
    def find_best_rates(self, all_rates: Dict[str, List[ShippingRate]]) -> Dict:
        """Find cheapest and fastest options"""
        all_quotes = []
        for carrier, rates in all_rates.items():
            for rate in rates:
                all_quotes.append({
                    'carrier': rate.carrier,
                    'service': rate.service_name,
                    'price': rate.price,
                    'delivery_days': rate.delivery_days,
                    'tracking': rate.tracking_included
                })
        
        if not all_quotes:
            return {"error": "No quotes found"}
        
        # Sort by price
        by_price = sorted(all_quotes, key=lambda x: x['price'])
        
        # Sort by delivery days (fastest first)
        by_speed = sorted(all_quotes, 
                         key=lambda x: self._parse_delivery_days(x['delivery_days']))
        
        return {
            'cheapest': by_price[0] if by_price else None,
            'fastest': by_speed[0] if by_speed else None,
            'all_quotes': all_quotes
        }
    
    def _parse_delivery_days(self, delivery_str: str) -> int:
        """Convert delivery string to minimum days"""
        import re
        numbers = re.findall(r'\d+', delivery_str)
        return int(numbers[0]) if numbers else 999

async def main():
    print("=" * 60)
    print("🚚 MULTI-CARRIER SHIPPING RATE COMPARATOR")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.getenv("TINYFISH_API_KEY")
    if not api_key:
        print("❌ Error: TINYFISH_API_KEY not found in .env file")
        print("Please add your API key to .env")
        return
    
    # Get user input
    print("\n📦 Enter package details:")
    try:
        weight = float(input("Weight (lbs): "))
        length = float(input("Length (inches): "))
        width = float(input("Width (inches): "))
        height = float(input("Height (inches): "))
        origin = input("Origin ZIP code: ")
        destination = input("Destination ZIP code: ")
    except ValueError:
        print("❌ Invalid input. Please enter numbers for dimensions.")
        return
    
    package = ShipmentPackage(
        weight_lbs=weight,
        length_in=length,
        width_in=width,
        height_in=height,
        origin_zip=origin,
        destination_zip=destination
    )
    
    # Ask which carriers to compare
    print("\n🔄 Which carriers to compare? (comma-separated: fedex,ups)")
    print("Or press Enter for all available carriers")
    carrier_input = input("Carriers: ").strip().lower()
    
    carriers = None
    if carrier_input:
        carriers = [c.strip() for c in carrier_input.split(',')]
    
    # Run comparison
    print("\n🔍 Getting rates from carriers...")
    print("⏳ This may take 30-60 seconds...\n")
    
    orchestrator = ShippingRateOrchestrator(api_key)
    
    try:
        # Get all rates
        all_rates = await orchestrator.compare_rates(package, carriers)
        
        # Find best options
        best = orchestrator.find_best_rates(all_rates)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        
        if 'error' in best:
            print(f"\n❌ {best['error']}")
            return
        
        # Prepare table for all quotes
        table_data = []
        for quote in sorted(best['all_quotes'], key=lambda x: x['price']):
            table_data.append([
                quote['carrier'].upper(),
                quote['service'][:30] + "..." if len(quote['service']) > 30 else quote['service'],
                f"${quote['price']:.2f}",
                quote['delivery_days']
            ])
        
        print("\n" + tabulate(table_data, 
                            headers=["Carrier", "Service", "Price", "Delivery"],
                            tablefmt="grid"))
        
        # Show best options
        print("\n" + "-" * 40)
        if best.get('cheapest'):
            c = best['cheapest']
            print(f"💰 CHEAPEST: {c['carrier'].upper()} - ${c['price']:.2f} ({c['delivery_days']})")
        
        if best.get('fastest') and best['fastest'] != best['cheapest']:
            f = best['fastest']
            print(f"⚡ FASTEST: {f['carrier'].upper()} - {f['delivery_days']} (${f['price']:.2f})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your package details and try again.")
    
    print("\n" + "=" * 60) 

if __name__ == "__main__":
    asyncio.run(main())

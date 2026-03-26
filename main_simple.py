"""Simplified version for testing"""

import asyncio
import sys
from colorama import init, Fore, Style

init(autoreset=True)

async def main_simple():
    print("=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}SHIPMENT RATE COMPARATOR (Simplified){Style.RESET_ALL}".center(70))
    print("=" * 70)
    
    print("\nThis is a simplified version to test the basic functionality.")
    print("\nEnter package details:")
    
    try:
        # Get input
        weight = float(input("  Weight (lbs): "))
        length = float(input("  Length (inches): "))
        width = float(input("  Width (inches): "))
        height = float(input("  Height (inches): "))
        origin = input("  Origin ZIP: ")
        destination = input("  Destination ZIP: ")
        
        print(f"\n{Fore.GREEN}Package Details:{Style.RESET_ALL}")
        print(f"  {weight} lbs, {length}x{width}x{height} inches")
        print(f"  From: {origin} → To: {destination}")
        
        print(f"\n{Fore.YELLOW}Fetching rates...{Style.RESET_ALL}")
        
        # Simulate fetching rates
        import random
        await asyncio.sleep(2)
        
        rates = [
            {"carrier": "FedEx", "service": "Ground", "price": 12.99, "days": 3},
            {"carrier": "FedEx", "service": "Express", "price": 24.99, "days": 1},
            {"carrier": "UPS", "service": "Ground", "price": 11.99, "days": 4},
            {"carrier": "UPS", "service": "Next Day", "price": 29.99, "days": 1},
            {"carrier": "USPS", "service": "Priority", "price": 15.99, "days": 2},
            {"carrier": "USPS", "service": "Ground", "price": 9.99, "days": 3}
        ]
        
        # Sort by price
        rates.sort(key=lambda x: x["price"])
        
        print(f"\n{Fore.GREEN}Results:{Style.RESET_ALL}")
        print("-" * 60)
        
        for i, rate in enumerate(rates, 1):
            if i == 1:
                price_color = Fore.GREEN
                print(f"{price_color}💰 CHEAPEST: {rate['carrier']} - {rate['service']}: ${rate['price']:.2f} ({rate['days']} days){Style.RESET_ALL}")
            else:
                print(f"  {i}. {rate['carrier']} - {rate['service']}: ${rate['price']:.2f} ({rate['days']} days)")
        
        print("-" * 60)
        print(f"\n{Fore.CYAN}✅ Comparison complete!{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main_simple())

"""Main application for shipment rate comparator"""

import asyncio
import sys
from colorama import init, Fore, Style
from typing import Optional

from config import Config
from models import ShipmentPackage
from orchestrator import ShippingRateOrchestrator
from display import DisplayManager
from utils.logger import setup_logger

init(autoreset=True)

class ShippingRateComparator:
    """Main application class"""
    
    def __init__(self):
        self.logger = setup_logger("main")
        self.display = DisplayManager()
        self.orchestrator = ShippingRateOrchestrator()
    
    def get_user_input(self) -> Optional[ShipmentPackage]:
        """Get shipment details from user"""
        self.display.print_header("🚚 SHIPMENT RATE COMPARATOR 🚚")
        
        try:
            print("\n📦 Enter package details:\n")
            
            # Weight
            weight = float(input("   Weight (lbs): ").strip())
            
            # Dimensions
            length = float(input("   Length (inches): ").strip())
            width = float(input("   Width (inches): ").strip())
            height = float(input("   Height (inches): ").strip())
            
            # ZIP codes
            origin = input("   Origin ZIP code: ").strip()
            destination = input("   Destination ZIP code: ").strip()
            
            # Optional declared value
            declared_input = input("   Declared value (optional, press Enter to skip): ").strip()
            declared_value = float(declared_input) if declared_input else None
            
            return ShipmentPackage(
                weight_lbs=weight,
                length_in=length,
                width_in=width,
                height_in=height,
                origin_zip=origin,
                destination_zip=destination,
                declared_value=declared_value
            )
            
        except KeyboardInterrupt:
            self.display.print_warning("\nOperation cancelled")
            return None
        except ValueError as e:
            self.display.print_error(f"Invalid input: {str(e)}")
            return None
        except Exception as e:
            self.display.print_error(f"Error: {str(e)}")
            return None
    
    async def run_comparison(self) -> None:
        """Run the rate comparison"""
        try:
            # Get user input
            package = self.get_user_input()
            if not package:
                return
            
            # Display package details
            self.display.print_package_details(package)
            
            # Run comparison
            self.display.print_subheader("Fetching Rates from Carriers")
            print("   This may take a few seconds...\n")
            
            result = await self.orchestrator.compare_rates(package)
            
            # Find best options
            best = self.orchestrator.find_best_rates(result)
            
            # Display results
            self.display.print_header("📊 COMPARISON RESULTS 📊")
            
            if result.rates:
                self.display.print_best_offers(best)
                self.display.print_all_quotes(best['all_quotes'])
                self.display.print_success(f"Found {len(result.rates)} shipping options")
            else:
                self.display.print_error("No rates could be retrieved")
                self.display.print_warning("Please check your package details and try again")
            
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            self.display.print_error(f"An error occurred: {str(e)}")

async def main():
    """Main entry point"""
    comparator = ShippingRateComparator()
    
    while True:
        await comparator.run_comparison()
        
        # Ask if user wants to compare another shipment
        print("\n" + "=" * 70)
        again = input("🔄 Compare another shipment? (y/n): ").strip().lower()
        if again != 'y':
            print(f"\n{Fore.GREEN}Thank you for using Shipment Rate Comparator!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
        sys.exit(0)

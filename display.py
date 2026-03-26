"""Display manager for console output"""

from tabulate import tabulate
from colorama import Fore, Style, init
from typing import Dict, List

init(autoreset=True)

class DisplayManager:
    """Manages console output formatting"""
    
    @staticmethod
    def print_header(title: str) -> None:
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(70)}{Style.RESET_ALL}")
        print("=" * 70)
    
    @staticmethod
    def print_subheader(text: str) -> None:
        """Print subheader"""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}▶ {text}{Style.RESET_ALL}")
        print("-" * 50)
    
    @staticmethod
    def print_package_details(package) -> None:
        """Print package details"""
        print(f"\n{Fore.GREEN}📦 Package Details:{Style.RESET_ALL}")
        print(f"   Weight: {package.weight_lbs} lbs")
        print(f"   Dimensions: {package.length_in} × {package.width_in} × {package.height_in} in")
        print(f"   Volume: {package.volume_cubic_inches:.0f} cu in")
        print(f"   From: {package.origin_zip}")
        print(f"   To: {package.destination_zip}")
        if package.declared_value:
            print(f"   Declared Value: ${package.declared_value:.2f}")
    
    @staticmethod
    def print_best_offers(best: Dict) -> None:
        """Print best offers"""
        
        if best['cheapest']:
            print(f"\n{Fore.GREEN}💰 CHEAPEST OPTION:{Style.RESET_ALL}")
            c = best['cheapest']
            print(f"   {Fore.WHITE}{c['carrier']} - {c['service']}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}Price: ${c['price']:.2f}{Style.RESET_ALL}")
            print(f"   Delivery: {c['delivery_days']} business days")
        
        if best['fastest'] and best['fastest'] != best['cheapest']:
            print(f"\n{Fore.CYAN}⚡ FASTEST OPTION:{Style.RESET_ALL}")
            f = best['fastest']
            print(f"   {Fore.WHITE}{f['carrier']} - {f['service']}{Style.RESET_ALL}")
            print(f"   Price: ${f['price']:.2f}")
            print(f"   {Fore.CYAN}Delivery: {f['delivery_days']} business days{Style.RESET_ALL}")
        
        if best.get('best_value') and best['best_value'] != best['cheapest']:
            print(f"\n{Fore.MAGENTA}🎯 BEST VALUE (Price per Day):{Style.RESET_ALL}")
            v = best['best_value']
            price_per_day = v['price'] / v['delivery_days']
            print(f"   {Fore.WHITE}{v['carrier']} - {v['service']}{Style.RESET_ALL}")
            print(f"   ${v['price']:.2f} / {v['delivery_days']} days = ${price_per_day:.2f}/day")
    
    @staticmethod
    def print_all_quotes(quotes: List[Dict]) -> None:
        """Print all quotes in a table"""
        if not quotes:
            return
        
        print(f"\n{Fore.YELLOW}📊 ALL SHIPPING QUOTES:{Style.RESET_ALL}")
        
        table_data = []
        for i, quote in enumerate(sorted(quotes, key=lambda x: x['price']), 1):
            if i == 1:
                price_color = Fore.GREEN
            elif i <= 3:
                price_color = Fore.YELLOW
            else:
                price_color = Fore.WHITE
            
            table_data.append([
                i,
                f"{Fore.CYAN}{quote['carrier']}{Style.RESET_ALL}",
                quote['service'][:35],
                f"{price_color}${quote['price']:.2f}{Style.RESET_ALL}",
                f"{quote['delivery_days']} days"
            ])
        
        headers = ["#", "Carrier", "Service", "Price", "Delivery"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print error message"""
        print(f"\n{Fore.RED}❌ ERROR: {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print success message"""
        print(f"\n{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message"""
        print(f"\n{Fore.YELLOW}⚠️  WARNING: {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print info message"""
        print(f"\n{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")

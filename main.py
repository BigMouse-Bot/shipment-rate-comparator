#!/usr/bin/env python3
"""
Shipment Rate Comparator for Indian E-commerce
Hackathon Submission
"""

import logging
from agent_orchestrator import RateOrchestrator

API_KEY = "sk-tinyfish-ItUBc-Vsr8i2Fcdy7Ww27FKr56QZNcwj"

def main():
    print("\n" + "="*70)
    print("             🚚 SHIPMENT RATE COMPARATOR - INDIA EDITION 🚚             ")
    print("="*70)
    
    # Get package details
    print("\n📦 Enter package details:\n")
    weight = float(input("   Weight (kg): "))
    length = float(input("   Length (cm): "))
    width = float(input("   Width (cm): "))
    height = float(input("   Height (cm): "))
    origin = input("   Origin Pincode (6 digits): ").strip()
    dest = input("   Destination Pincode (6 digits): ").strip()
    declared_value = input("   Declared value (optional, press Enter to skip): ").strip()
    
    # Display package summary
    print(f"\n📦 Package Details:")
    print(f"   Weight: {weight} kg")
    print(f"   Dimensions: {length} × {width} × {height} cm")
    print(f"   Volume: {length * width * height} cu cm")
    print(f"   From Pincode: {origin}")
    print(f"   To Pincode: {dest}")
    
    # Fetch rates
    print("\n▶ Fetching Rates from Indian Carriers")
    print("-" * 50)
    print("   Comparing DTDC, Blue Dart, Delhivery, India Post...\n")
    
    orchestrator = RateOrchestrator(API_KEY)
    results = orchestrator.compare_rates(weight, origin, dest)
    
    # Display results
    print("\n" + "="*70)
    print("                        📊 COMPARISON RESULTS 📊                        ")
    print("="*70)
    
    # Sort by price (cheapest first)
    valid_results = [r for r in results if r.get('price')]
    valid_results.sort(key=lambda x: x.get('price', float('inf')))
    
    if valid_results:
        print(f"\n{'Carrier':<15} {'Service':<15} {'Price':<15} {'Delivery':<15}")
        print("-" * 60)
        for r in valid_results:
            price_str = r.get('price_display', 'N/A')
            print(f"{r['carrier']:<15} {r['service']:<15} {price_str:<15} {r['delivery_time']:<15}")
        
        # Show best option
        best = valid_results[0]
        print(f"\n🏆 BEST RATE: {best['carrier']} - {best['service']} at {best['price_display']}")
        print(f"   Estimated delivery: {best['delivery_time']}")
        
        # Show DTDC options if available
        dtdc_result = next((r for r in results if r['carrier'] == 'DTDC'), None)
        if dtdc_result and dtdc_result.get('all_options'):
            print(f"\n📦 DTDC Additional Options:")
            for opt in dtdc_result['all_options']:
                print(f"   • {opt.get('service', 'Service')}: ₹{opt.get('estimated_price', 'N/A')} - {opt.get('delivery_time', 'N/A')}")
    else:
        print("\n❌ ERROR: No rates could be retrieved")
        print("\n⚠️  WARNING: Please check your pincodes and try again")
    
    print("\n" + "="*70)
    choice = input("\n🔄 Compare another shipment? (y/n): ").lower()
    if choice == 'y':
        main()
    else:
        print("\nDhanyavaad! Thank you for using Shipment Rate Comparator!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)  # Reduce verbosity
    main()

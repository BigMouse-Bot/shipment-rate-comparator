#!/usr/bin/env python3
"""
Shipment Rate Comparator for Indian E-commerce - Simple Working Version
"""

import json
import requests
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "sk-tinyfish-ItUBc-Vsr8i2Fcdy7Ww27FKr56QZNcwj"
BASE_URL = "https://agent.tinyfish.ai"

def get_dtdc_rates(weight_kg: float, origin: str, dest: str) -> Optional[Dict]:
    """Get DTDC rates directly"""
    
    goal = f"""
    Find DTDC domestic e-commerce shipping rate for a {weight_kg}kg parcel.
    Origin pincode: {origin}
    Destination pincode: {dest}
    
    Return JSON with:
    - primary_service: {{"carrier_name":"DTDC","service":"service name","estimated_price":price,"delivery_time":"X days"}}
    - additional_options: list of other services with estimated_price and delivery_time
    """
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"url": "https://www.dtdc.in", "goal": goal, "browser_profile": "stealth"}
    
    try:
        response = requests.post(f"{BASE_URL}/v1/automation/run-sse", headers=headers, json=payload, stream=True, timeout=180)
        
        if response.status_code != 200:
            return None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '):
                    event = json.loads(line_str[6:])
                    if event.get('type') == 'COMPLETE' and event.get('status') == 'COMPLETED':
                        return event.get('result')
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def main():
    print("\n" + "="*70)
    print("             🚚 SHIPMENT RATE COMPARATOR - INDIA EDITION 🚚             ")
    print("="*70)
    
    print("\n📦 Enter package details:\n")
    weight = float(input("   Weight (kg): "))
    length = float(input("   Length (cm): "))
    width = float(input("   Width (cm): "))
    height = float(input("   Height (cm): "))
    origin = input("   Origin Pincode (6 digits): ").strip()
    dest = input("   Destination Pincode (6 digits): ").strip()
    
    print(f"\n📦 Package: {weight}kg, {origin} → {dest}")
    print("\n▶ Fetching DTDC Rates...\n")
    
    result = get_dtdc_rates(weight, origin, dest)
    
    print("\n" + "="*70)
    print("                        📊 COMPARISON RESULTS 📊                        ")
    print("="*70)
    
    if result and "primary_service" in result:
        primary = result["primary_service"]
        print(f"\n✅ DTDC {primary.get('service', 'Service')}")
        print(f"   Price: ₹{primary.get('estimated_price', 0):,.2f}")
        print(f"   Delivery: {primary.get('delivery_time', 'N/A')}")
        
        if "additional_options" in result:
            print(f"\n📦 Other DTDC Options:")
            for opt in result["additional_options"]:
                print(f"   • {opt.get('service', 'Service')}: ₹{opt.get('estimated_price', 'N/A')} - {opt.get('delivery_time', 'N/A')}")
    else:
        print("\n❌ Could not fetch rates. Please try again.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

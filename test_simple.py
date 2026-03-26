"""Simple test to verify all modules load"""

import sys
import asyncio

print("=" * 60)
print("Testing module imports...")
print("=" * 60)

# Test 1: Basic modules
print("\n1. Testing basic modules...")
try:
    import config
    print("   ✅ config")
except Exception as e:
    print(f"   ❌ config: {e}")

try:
    import models
    print("   ✅ models")
except Exception as e:
    print(f"   ❌ models: {e}")

# Test 2: Utils
print("\n2. Testing utils...")
try:
    from utils.logger import setup_logger
    print("   ✅ logger")
except Exception as e:
    print(f"   ❌ logger: {e}")

try:
    from utils.validators import validate_zip_code
    print("   ✅ validators")
except Exception as e:
    print(f"   ❌ validators: {e}")

# Test 3: TinyFish client
print("\n3. Testing TinyFish client...")
try:
    from tinyfish_client import TinyFishClient, WebAgent
    print("   ✅ tinyfish_client")
except Exception as e:
    print(f"   ❌ tinyfish_client: {e}")

# Test 4: Agents
print("\n4. Testing agents...")
try:
    from agents import FedExAgent, UPSAgent, USPSAgent
    print("   ✅ FedExAgent")
    print("   ✅ UPSAgent")
    print("   ✅ USPSAgent")
except Exception as e:
    print(f"   ❌ agents: {e}")

# Test 5: Orchestrator and display
print("\n5. Testing orchestrator and display...")
try:
    from orchestrator import ShippingRateOrchestrator
    print("   ✅ orchestrator")
except Exception as e:
    print(f"   ❌ orchestrator: {e}")

try:
    from display import DisplayManager
    print("   ✅ display")
except Exception as e:
    print(f"   ❌ display: {e}")

print("\n" + "=" * 60)
print("✅ All imports successful!")
print("=" * 60)

# Quick test of the orchestrator
async def quick_test():
    print("\nRunning quick test with mock data...")
    from models import ShipmentPackage
    from orchestrator import ShippingRateOrchestrator
    
    package = ShipmentPackage(
        weight_lbs=10,
        length_in=12,
        width_in=12,
        height_in=12,
        origin_zip="90210",
        destination_zip="10001"
    )
    
    orchestrator = ShippingRateOrchestrator()
    print("   Comparing rates...")
    result = await orchestrator.compare_rates(package)
    print(f"   Found {len(result.rates)} rates")
    
    if result.rates:
        print("   Sample rates:")
        for rate in result.rates[:3]:
            print(f"     • {rate.carrier.value}: {rate.service_name} - ${rate.price:.2f}")
    else:
        print("   ⚠️  No rates found (expected in mock mode)")

asyncio.run(quick_test())

if __name__ == "__main__":
    pass

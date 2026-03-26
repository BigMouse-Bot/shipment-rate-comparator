"""Simple environment test"""

import sys
import os

print("=" * 60)
print("🔧 ENVIRONMENT SETUP TEST")
print("=" * 60)

# Test Python version
print("\n🐍 Checking Python version...")
version = sys.version_info
print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")

# Test required packages
print("\n📦 Checking dependencies...")
packages = ['dotenv', 'pandas', 'tabulate', 'colorama', 'pydantic', 'aiohttp']
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f"   ✅ {pkg}")
    except ImportError:
        print(f"   ❌ {pkg} - NOT INSTALLED")

# Test .env file
print("\n🔑 Checking environment configuration...")
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('TINYFISH_API_KEY')
if api_key:
    if api_key == 'your_api_key_here':
        print("   ⚠️  API key is placeholder - update .env")
    else:
        print(f"   ✅ API key found: {api_key[:8]}...")
else:
    print("   ❌ No API key found")

print("\n" + "=" * 60)

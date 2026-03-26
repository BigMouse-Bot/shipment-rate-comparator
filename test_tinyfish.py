"""Test TinyFish API connection"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_tinyfish_connection():
    print("\n" + "=" * 60)
    print("🌐 Testing TinyFish API Connection")
    print("=" * 60)
    
    api_key = os.getenv('TINYFISH_API_KEY')
    
    if not api_key:
        print("\n❌ No API key found in .env file!")
        return False
    
    if api_key == 'your_api_key_here':
        print("\n⚠️  API key is placeholder! Please update .env")
        return False
    
    print(f"\n✅ API key found: {api_key[:8]}...")
    
    try:
        from tinyfish_client import TinyFishClient
        client = TinyFishClient(api_key=api_key)
        
        print("\n🤖 Creating test agent...")
        agent = await client.create_agent(headless=True, timeout=10000)
        
        print("🌍 Navigating to test page...")
        await agent.goto("https://httpbin.org/status/200")
        
        print("✅ Navigation successful!")
        
        await agent.close()
        await client.close()
        
        print("\n✅ TinyFish API connection successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ TinyFish API test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_tinyfish_connection())

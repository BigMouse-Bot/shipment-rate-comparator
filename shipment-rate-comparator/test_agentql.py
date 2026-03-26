import os
from agentql import AgentQLClient

# Check if API key is set
api_key = os.getenv("AGENTQL_API_KEY")
if not api_key:
    print("❌ AGENTQL_API_KEY not set in environment")
    print("Please set it with: export AGENTQL_API_KEY=your_key")
else:
    print(f"✅ AGENTQL_API_KEY is set")
    print("AgentQL is ready to use!")

"""Application configuration"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # TinyFish API - USE THE CORRECT KEY FROM .env
    TINYFISH_API_KEY = os.getenv('TINYFISH_API_KEY', '')
    TINYFISH_API_URL = os.getenv('TINYFISH_API_URL', 'https://agent.tinyfish.ai')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Carrier URLs
    CARRIER_URLS = {
        'dtdc': 'https://www.dtdc.in',
        'bluedart': 'https://www.bluedart.com',
        'delhivery': 'https://www.delhivery.com',
        'indiapost': 'https://www.indiapost.gov.in'
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TINYFISH_API_KEY:
            raise ValueError("TINYFISH_API_KEY is required. Set it in .env file")
        if cls.TINYFISH_API_KEY == 'your_actual_key_here':
            raise ValueError("Please update .env with your actual TinyFish API key")
        return True

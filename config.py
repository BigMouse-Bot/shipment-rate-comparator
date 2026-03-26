"""Application configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # TinyFish API
    TINYFISH_API_KEY = os.getenv('TINYFISH_API_KEY', '')
    TINYFISH_API_URL = os.getenv('TINYFISH_API_URL', 'https://api.tinyfish.ai/v1')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Carrier URLs
    CARRIER_URLS = {
        'fedex': 'https://www.fedex.com/en-us/shipping/rates.html',
        'ups': 'https://www.ups.com/us/en/shipping/calculate-rates.page',
        'usps': 'https://postcalc.usps.com/'
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TINYFISH_API_KEY:
            raise ValueError("TINYFISH_API_KEY is required. Set it in .env file")
        if cls.TINYFISH_API_KEY == 'your_api_key_here':
            raise ValueError("Please update .env with your actual TinyFish API key")
        return True

#!/usr/bin/env python3
"""
TinyFish API Client for Shipment Rate Comparator
"""

import json
import requests
import logging
from typing import Dict, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TinyFishClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://agent.tinyfish.ai"
        
    def scrape_rates(self, url: str, goal: str, timeout: int = 180) -> Optional[Dict]:
        """Call TinyFish API to scrape shipping rates"""
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "url": url,
            "goal": goal,
            "browser_profile": "stealth"
        }
        
        try:
            logger.info(f"Calling TinyFish API for {url}...")
            
            response = requests.post(
                f"{self.base_url}/v1/automation/run-sse",
                headers=headers,
                json=payload,
                stream=True,
                timeout=timeout
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
            
            # Parse SSE stream
            result_data = None
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '):
                    try:
                        event = json.loads(line_str[6:])
                        event_type = event.get('type')
                        
                        if event_type == 'PROGRESS':
                            purpose = event.get('purpose', 'Working...')
                            logger.info(f"🔍 {purpose}")
                            
                        elif event_type == 'COMPLETE':
                            if event.get('status') == 'COMPLETED':
                                result_data = event.get('result')
                                logger.info("✅ API call completed successfully")
                                break
                            else:
                                logger.error(f"❌ API failed: {event.get('status')}")
                                return None
                                
                        elif event_type == 'ERROR':
                            logger.error(f"❌ API error: {event.get('message', 'Unknown error')}")
                            return None
                            
                    except json.JSONDecodeError:
                        continue
            
            return result_data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    def get_dtdc_rates(self, weight_kg: float, origin_pincode: str, dest_pincode: str) -> Optional[Dict]:
        """Get DTDC shipping rates"""
        goal = f"""
        Find DTDC domestic e-commerce shipping rate for a {weight_kg}kg parcel.
        Origin pincode: {origin_pincode}
        Destination pincode: {dest_pincode}
        
        Use DTDC rate calculator or integrated tools like ClickPost to find exact rates.
        Return JSON with:
        - primary_service: {{"carrier_name":"DTDC","service":"service name","estimated_price":price in INR,"delivery_time":"X days","weight_kg":{weight_kg},"origin_pincode":"{origin_pincode}","destination_pincode":"{dest_pincode}"}}
        - additional_options: list of other service options with estimated_price and delivery_time
        """
        
        return self.scrape_rates("https://www.dtdc.in", goal)
    
    def get_bluedart_rates(self, weight_kg: float, origin_pincode: str, dest_pincode: str) -> Optional[Dict]:
        """Get Blue Dart shipping rates"""
        goal = f"""
        Find Blue Dart domestic shipping rate for a {weight_kg}kg e-commerce parcel.
        Origin: {origin_pincode}, Destination: {dest_pincode}
        
        Look for rate calculator or tariff section.
        Return JSON with carrier_name, service, estimated_price in INR, delivery_time in days.
        """
        
        return self.scrape_rates("https://www.bluedart.com", goal)
    
    def get_delhivery_rates(self, weight_kg: float, origin_pincode: str, dest_pincode: str) -> Optional[Dict]:
        """Get Delhivery shipping rates"""
        goal = f"""
        Find Delhivery domestic shipping rate for a {weight_kg}kg parcel.
        Origin pincode: {origin_pincode}
        Destination pincode: {dest_pincode}
        
        Return JSON with carrier_name, service, estimated_price in INR, delivery_time in days.
        """
        
        return self.scrape_rates("https://www.delhivery.com", goal)
    
    def get_indiapost_rates(self, weight_kg: float, origin_pincode: str, dest_pincode: str) -> Optional[Dict]:
        """Get India Post Speed Post rates"""
        goal = f"""
        Find India Post Speed Post rate for a {weight_kg}kg domestic parcel.
        Use official rate calculator or rate card.
        
        Return JSON with carrier_name: "India Post", service: "Speed Post", 
        estimated_price in INR, delivery_time in days.
        """
        
        return self.scrape_rates("https://www.indiapost.gov.in", goal)

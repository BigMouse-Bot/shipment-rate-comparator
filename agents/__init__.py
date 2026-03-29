"""Carrier agents package - Indian carriers"""

from agents.base_agent import BaseCarrierAgent
from agents.dtdc_agent import DTDCAgent
from agents.bluedart_agent import BlueDartAgent
from agents.delhivery_agent import DelhiveryAgent
from agents.indiapost_agent import IndiaPostAgent

# Optional: Keep FedEx if you want international comparison
# from agents.fedex_agent import FedExAgent

__all__ = [
    'BaseCarrierAgent',
    'DTDCAgent',
    'BlueDartAgent',
    'DelhiveryAgent',
    'IndiaPostAgent'
]

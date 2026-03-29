"""Carrier agents package - Indian carriers"""

from agents.base_agent import BaseCarrierAgent
from agents.dtdc_agent import DTDCAgent

# Only import available agents
try:
    from agents.bluedart_agent import BlueDartAgent
except ImportError:
    BlueDartAgent = None

try:
    from agents.delhivery_agent import DelhiveryAgent
except ImportError:
    DelhiveryAgent = None

try:
    from agents.indiapost_agent import IndiaPostAgent
except ImportError:
    IndiaPostAgent = None

__all__ = [
    'BaseCarrierAgent',
    'DTDCAgent',
    'BlueDartAgent',
    'DelhiveryAgent',
    'IndiaPostAgent'
]

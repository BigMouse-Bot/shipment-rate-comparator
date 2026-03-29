"""Input validation for Indian addresses"""

import re
from typing import Tuple, Optional

def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode (6 digits)"""
    return bool(re.match(r'^\d{6}$', pincode))

def validate_weight(weight: float) -> Tuple[bool, Optional[str]]:
    """Validate package weight"""
    if weight <= 0:
        return False, "Weight must be greater than 0"
    if weight > 50:
        return False, "Weight exceeds 50kg (max for most Indian carriers)"
    return True, None

def validate_dimensions(length: float, width: float, height: float) -> Tuple[bool, Optional[str]]:
    """Validate package dimensions"""
    if any(d <= 0 for d in [length, width, height]):
        return False, "All dimensions must be greater than 0"
    if any(d > 200 for d in [length, width, height]):
        return False, "Dimensions exceed 200cm (max for most Indian carriers)"
    return True, None

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return text.strip().replace('\n', ' ').replace('\r', '')

def format_pincode(pincode: str) -> str:
    """Format pincode with proper spacing"""
    pincode = re.sub(r'\D', '', pincode)
    if len(pincode) == 6:
        return f"{pincode[:3]} {pincode[3:]}"
    return pincode

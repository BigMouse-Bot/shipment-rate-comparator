"""Input validation utilities"""

import re
from typing import Optional

def validate_zip_code(zip_code: str) -> bool:
    """Validate US ZIP code format"""
    pattern = r'^\d{5}(-\d{4})?$'
    return bool(re.match(pattern, zip_code))

def validate_weight(weight: float) -> bool:
    """Validate package weight"""
    return 0.1 <= weight <= 150.0

def validate_dimensions(length: float, width: float, height: float) -> bool:
    """Validate package dimensions"""
    return all(0.5 <= dim <= 108.0 for dim in [length, width, height])

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove trailing slash that was causing the error
    return text.strip().replace('\n', ' ').replace('\r', '')

"""Data models for shipment rate comparator - India Edition"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ServiceLevel(Enum):
    """Shipping service levels"""
    SAME_DAY = "Same Day"
    NEXT_DAY = "Next Day"
    TWO_DAY = "2 Day"
    THREE_DAY = "3 Day"
    GROUND = "Ground"
    ECONOMY = "Economy"
    EXPRESS = "Express"
    STANDARD = "Standard"

class Carrier(Enum):
    """Supported carriers - India focus"""
    DTDC = "DTDC"
    BLUEDART = "Blue Dart"
    DELHIVERY = "Delhivery"
    INDIA_POST = "India Post"

@dataclass
class ShipmentPackage:
    """Represents a package to be shipped"""
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float
    origin_pincode: str
    destination_pincode: str
    declared_value: Optional[float] = None
    is_residential: bool = True
    
    def __post_init__(self):
        """Validate package data"""
        if self.weight_kg <= 0:
            raise ValueError("Weight must be positive")
        if self.length_cm <= 0 or self.width_cm <= 0 or self.height_cm <= 0:
            raise ValueError("Dimensions must be positive")
        if len(self.origin_pincode) != 6 or len(self.destination_pincode) != 6:
            raise ValueError("Indian pincodes must be 6 digits")
    
    @property
    def volume_cubic_cm(self) -> float:
        """Calculate package volume in cubic cm"""
        return self.length_cm * self.width_cm * self.height_cm

@dataclass
class ShippingRate:
    """Represents a shipping rate quote in INR"""
    carrier: Carrier
    service_name: str
    service_level: ServiceLevel
    price_inr: float
    delivery_days: int
    estimated_delivery_date: Optional[str] = None
    tracking_included: bool = True
    url: str = ""
    insurance_cost: float = 0.0
    
    def __post_init__(self):
        """Ensure price is float"""
        self.price_inr = float(self.price_inr)
    
    @property
    def formatted_price(self) -> str:
        """Return formatted price in INR"""
        return f"₹{self.price_inr:.2f}"
    
    def __lt__(self, other):
        """Compare by price for sorting"""
        return self.price_inr < other.price_inr

@dataclass
class ComparisonResult:
    """Result of rate comparison"""
    package: ShipmentPackage
    rates: List[ShippingRate] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def cheapest(self) -> Optional[ShippingRate]:
        """Get cheapest rate"""
        if not self.rates:
            return None
        return min(self.rates, key=lambda x: x.price_inr)
    
    @property
    def fastest(self) -> Optional[ShippingRate]:
        """Get fastest rate"""
        if not self.rates:
            return None
        return min(self.rates, key=lambda x: x.delivery_days)

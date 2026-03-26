# models.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum

class ServiceLevel(Enum):
    """Shipping service levels"""
    SAME_DAY = "Same Day"
    NEXT_DAY = "Next Day"
    TWO_DAY = "2 Day"
    THREE_DAY = "3 Day"
    GROUND = "Ground"
    ECONOMY = "Economy"

class Carrier(Enum):
    """Supported carriers"""
    FEDEX = "FedEx"
    UPS = "UPS"
    USPS = "USPS"

@dataclass
class ShipmentPackage:
    """Represents a package to be shipped"""
    weight_lbs: float
    length_in: float
    width_in: float
    height_in: float
    origin_zip: str
    destination_zip: str
    declared_value: Optional[float] = None
    is_residential: bool = True
    
    def __post_init__(self):
        """Validate package data"""
        if self.weight_lbs <= 0:
            raise ValueError("Weight must be positive")
        if self.length_in <= 0 or self.width_in <= 0 or self.height_in <= 0:
            raise ValueError("Dimensions must be positive")
        if len(self.origin_zip) < 5 or len(self.destination_zip) < 5:
            raise ValueError("ZIP codes must be at least 5 characters")
    
    @property
    def volume_cubic_inches(self) -> float:
        """Calculate package volume"""
        return self.length_in * self.width_in * self.height_in
    
    @property
    def dimensional_weight(self) -> float:
        """Calculate DIM weight (standard divisor 166)"""
        return self.volume_cubic_inches / 166.0

@dataclass
class ShippingRate:
    """Represents a shipping rate quote"""
    carrier: Carrier
    service_name: str
    service_level: ServiceLevel
    price: float
    delivery_days: int
    estimated_delivery_date: Optional[str] = None
    tracking_included: bool = True
    url: str = ""
    insurance_cost: float = 0.0
    
    def __post_init__(self):
        """Ensure price is float"""
        self.price = float(self.price)
    
    @property
    def formatted_price(self) -> str:
        """Return formatted price"""
        return f"${self.price:.2f}"
    
    def __lt__(self, other):
        """Compare by price for sorting"""
        return self.price < other.price

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
        return min(self.rates, key=lambda x: x.price)
    
    @property
    def fastest(self) -> Optional[ShippingRate]:
        """Get fastest rate"""
        if not self.rates:
            return None
        return min(self.rates, key=lambda x: x.delivery_days)
    
    @property
    def best_value(self) -> Optional[ShippingRate]:
        """Get best value (price per day)"""
        if not self.rates:
            return None
        return min(self.rates, key=lambda x: x.price / x.delivery_days)
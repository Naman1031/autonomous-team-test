from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class DiscountType(str, Enum):
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"

@dataclass
class Coupon:
    id: str
    code: str
    discount_type: DiscountType
    discount_value: float
    expiration_date: Optional[datetime] = None
    min_order_threshold: Optional[float] = None
    max_usage_limit: Optional[int] = None
    current_usage_count: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

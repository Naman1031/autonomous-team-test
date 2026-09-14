import uuid
from datetime import datetime
from typing import Dict, Optional
from src.models.coupon import Coupon, DiscountType

class DuplicateCouponError(Exception):
    def __init__(self, code: str):
        super().__init__(f"Coupon code '{code}' already exists.")
        self.code = code

class CouponService:
    def __init__(self):
        self._coupons: Dict[str, Coupon] = {}

    def create_coupon(
        self,
        code: str,
        discount_type: str,
        discount_value: float,
        expiration_date: Optional[str] = None,
        min_order_threshold: Optional[float] = None,
        max_usage_limit: Optional[int] = None
    ) -> Coupon:
        normalized_code = code.strip().upper()
        if normalized_code in self._coupons:
            raise DuplicateCouponError(normalized_code)

        parsed_exp = None
        if expiration_date:
            parsed_exp = datetime.fromisoformat(expiration_date)

        coupon = Coupon(
            id=str(uuid.uuid4()),
            code=normalized_code,
            discount_type=DiscountType(discount_type.upper()),
            discount_value=discount_value,
            expiration_date=parsed_exp,
            min_order_threshold=min_order_threshold,
            max_usage_limit=max_usage_limit,
            current_usage_count=0,
            is_active=True
        )
        self._coupons[normalized_code] = coupon
        return coupon

    def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        return self._coupons.get(code.strip().upper())

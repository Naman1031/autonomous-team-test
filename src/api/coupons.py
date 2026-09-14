from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Coupon Discount Service")
COUPONS_DB: Dict[str, Dict[str, Any]] = {}

class CouponValidationRequest(BaseModel):
    code: str

class CouponValidationResponse(BaseModel):
    valid: bool
    code: str
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    message: Optional[str] = None

class CouponApplyRequest(BaseModel):
    code: str
    order_subtotal: float

class CouponApplyResponse(BaseModel):
    code: str
    original_subtotal: float
    discount_amount: float
    final_subtotal: float

def is_coupon_valid(coupon: Dict[str, Any], now: Optional[datetime] = None) -> Tuple[bool, str]:
    if now is None:
        now = datetime.now(timezone.utc)
    if coupon.get("max_usages") is not None and coupon.get("current_usages", 0) >= coupon["max_usages"]:
        return False, "Coupon usage limit reached"
    starts_at = coupon.get("starts_at")
    if starts_at and now < starts_at:
        return False, "Coupon is not active yet"
    expires_at = coupon.get("expires_at")
    if expires_at and now > expires_at:
        return False, "Coupon has expired"
    return True, "Coupon is valid"

@app.post("/api/v1/coupons/validate", response_model=CouponValidationResponse)
def validate_coupon(payload: CouponValidationRequest):
    code = payload.code.strip()
    coupon = COUPONS_DB.get(code)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon code does not exist")
    valid, message = is_coupon_valid(coupon)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return CouponValidationResponse(valid=True, code=coupon["code"], discount_type=coupon["discount_type"], discount_value=coupon["discount_value"], message=message)

@app.post("/api/v1/coupons/apply", response_model=CouponApplyResponse)
def apply_coupon(payload: CouponApplyRequest):
    code = payload.code.strip()
    coupon = COUPONS_DB.get(code)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon code does not exist")
    valid, message = is_coupon_valid(coupon)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    subtotal = payload.order_subtotal
    if coupon["discount_type"] == "PERCENTAGE":
        discount = round(subtotal * (coupon["discount_value"] / 100.0), 2)
    elif coupon["discount_type"] == "FIXED_AMOUNT":
        discount = round(min(subtotal, coupon["discount_value"]), 2)
    else:
        discount = 0.0
    final_subtotal = round(max(0.0, subtotal - discount), 2)
    return CouponApplyResponse(code=coupon["code"], original_subtotal=subtotal, discount_amount=discount, final_subtotal=final_subtotal)

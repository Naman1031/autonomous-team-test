from fastapi import FastAPI, HTTPException, status, Path
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from uuid import uuid4, UUID
from datetime import datetime

app = FastAPI()

# In‑memory store for coupons (id -> coupon data)
_coupons_by_id = {}
_coupons_by_code = {}

class CouponCreateRequest(BaseModel):
    code: str = Field(..., min_length=1)
    discount_type: Literal["PERCENTAGE", "FIXED_AMOUNT"]
    discount_value: float = Field(..., gt=0)
    min_order_amount: Optional[float] = None
    expires_at: Optional[datetime] = None

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if values.get('discount_type') == 'PERCENTAGE' and not (0 < v <= 100):
            raise ValueError('percentage discount must be between 0 and 100')
        return v

class CouponExpirationRequest(BaseModel):
    expires_at: datetime

class CouponResponse(BaseModel):
    id: UUID
    code: str
    discount_type: str
    discount_value: float
    min_order_amount: Optional[float]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@app.post("/api/v1/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(payload: CouponCreateRequest):
    # Duplicate code check
    if payload.code in _coupons_by_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    now = datetime.utcnow()
    coupon_id = uuid4()
    coupon = {
        "id": coupon_id,
        "code": payload.code,
        "discount_type": payload.discount_type,
        "discount_value": payload.discount_value,
        "min_order_amount": payload.min_order_amount,
        "expires_at": payload.expires_at,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    _coupons_by_id[coupon_id] = coupon
    _coupons_by_code[payload.code] = coupon
    return CouponResponse(**coupon)

@app.patch("/api/v1/coupons/{coupon_id}/expiration", response_model=CouponResponse)
def set_coupon_expiration(
    coupon_id: UUID = Path(..., description="The UUID of the coupon to update"),
    payload: CouponExpirationRequest = None,
):
    """Update the expiration date of an existing coupon.

    The request body must contain an ``expires_at`` field. If the supplied date
    is in the past relative to the current UTC time, the request is rejected.
    """
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="expires_at is required")

    # Retrieve existing coupon
    coupon = _coupons_by_id.get(coupon_id)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")

    now = datetime.utcnow()
    if payload.expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date")

    # Update coupon
    coupon["expires_at"] = payload.expires_at
    coupon["updated_at"] = now
    return CouponResponse(**coupon)

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict

router = APIRouter()

class CouponCreate(BaseModel):
    code: str = Field(..., max_length=50)
    discount_type: str = Field(..., regex="^(FIXED|PERCENT)$")
    discount_value: float = Field(..., gt=0)
    valid_from: datetime
    valid_to: datetime

    @validator('valid_to')
    def check_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_to must be after valid_from')
        return v

class CouponResponse(CouponCreate):
    id: uuid.UUID
    status: str = "CREATED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# In‑memory store for demonstration purposes (replace with DB in production)
_coupons: Dict[uuid.UUID, CouponResponse] = {}

@router.post("/coupons", response_model=CouponResponse)
def create_coupon(coupon: CouponCreate):
    # Ensure coupon code uniqueness
    if any(existing.code == coupon.code for existing in _coupons.values()):
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    coupon_id = uuid.uuid4()
    new_coupon = CouponResponse(id=coupon_id, **coupon.dict())
    _coupons[coupon_id] = new_coupon
    return new_coupon

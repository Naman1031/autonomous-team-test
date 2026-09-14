from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional, Dict

router = APIRouter()

class Coupon(BaseModel):
    code: str = Field(..., min_length=1)
    discount_type: str = Field(..., regex="^(PERCENTAGE|FIXED)$")
    discount_value: float = Field(..., gt=0)
    start_date: date
    end_date: date
    usage_limit: Optional[int] = None
    usage_count: int = 0
    active: bool = True

    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# In‑memory store for demonstration purposes
_coupon_store: Dict[str, Coupon] = {}

@router.post("/coupons", status_code=status.HTTP_201_CREATED)
def create_coupon(coupon: Coupon):
    if coupon.code in _coupon_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    _coupon_store[coupon.code] = coupon
    return {"message": "Coupon created successfully", "code": coupon.code}

app = FastAPI()
app.include_router(router)

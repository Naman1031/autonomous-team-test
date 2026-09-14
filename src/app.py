from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
import uuid
from datetime import datetime

app = FastAPI(title="Coupon Discount Service")

coupons_db: Dict[str, dict] = {}

class PercentageCouponRequest(BaseModel):
    code: str
    percentage: float

    @field_validator('code')
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Coupon code cannot be empty')
        return v.strip().upper()

    @field_validator('percentage')
    def validate_percentage(cls, v):
        if v < 1.0 or v > 100.0:
            raise ValueError('Percentage discount must be between 1 and 100')
        return v

@app.post("/api/v1/admin/coupons/percentage", status_code=status.HTTP_201_CREATED)
def create_percentage_coupon(request: PercentageCouponRequest):
    if request.code in coupons_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon with code '{request.code}' already exists"
        )

    coupon_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    coupon = {
        "id": coupon_id,
        "code": request.code,
        "discount_type": "PERCENTAGE",
        "discount_value": request.percentage,
        "max_usages": None,
        "current_usages": 0,
        "starts_at": None,
        "expires_at": None,
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now
    }
    
    coupons_db[request.code] = coupon
    return {
        "message": "Percentage coupon created successfully",
        "coupon": coupon
    }

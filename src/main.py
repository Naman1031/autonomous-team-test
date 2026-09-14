from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict
import uuid
from datetime import datetime

app = FastAPI(title="Coupon Discount Service")

coupons_db: Dict[str, dict] = {}

class CreateFixedCouponRequest(BaseModel):
    code: str = Field(..., min_length=1)
    amount: float

@app.post("/api/v1/admin/coupons/fixed", status_code=status.HTTP_201_CREATED)
def create_fixed_coupon(payload: CreateFixedCouponRequest):
    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount amount must be greater than zero."
        )
    
    code_upper = payload.code.strip().upper()
    if not code_upper:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code cannot be empty."
        )
        
    for existing in coupons_db.values():
        if existing["code"] == code_upper:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon code already exists."
            )
            
    coupon_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    coupon = {
        "id": coupon_id,
        "code": code_upper,
        "discount_type": "FIXED_AMOUNT",
        "discount_value": payload.amount,
        "max_usages": None,
        "current_usages": 0,
        "starts_at": None,
        "expires_at": None,
        "created_at": now,
        "updated_at": now
    }
    coupons_db[coupon_id] = coupon
    return coupon

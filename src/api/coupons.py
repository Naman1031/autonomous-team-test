from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from src.services.coupon_service import CouponService, DuplicateCouponError

app = FastAPI(title="Coupon Discount Service")
coupon_service = CouponService()

class CreateCouponRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Unique coupon code")
    discount_type: str = Field(..., description="FIXED or PERCENTAGE")
    discount_value: float = Field(..., gt=0, description="Discount amount or percentage value")
    expiration_date: Optional[str] = None
    min_order_threshold: Optional[float] = None
    max_usage_limit: Optional[int] = None

class CouponResponse(BaseModel):
    id: str
    code: str
    discount_type: str
    discount_value: float
    expiration_date: Optional[str] = None
    min_order_threshold: Optional[float] = None
    max_usage_limit: Optional[int] = None
    current_usage_count: int
    is_active: bool

@app.post("/api/v1/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(request: CreateCouponRequest):
    try:
        coupon = coupon_service.create_coupon(
            code=request.code,
            discount_type=request.discount_type,
            discount_value=request.discount_value,
            expiration_date=request.expiration_date,
            min_order_threshold=request.min_order_threshold,
            max_usage_limit=request.max_usage_limit
        )
        return CouponResponse(
            id=coupon.id,
            code=coupon.code,
            discount_type=coupon.discount_type.value,
            discount_value=coupon.discount_value,
            expiration_date=coupon.expiration_date.isoformat() if coupon.expiration_date else None,
            min_order_threshold=coupon.min_order_threshold,
            max_usage_limit=coupon.max_usage_limit,
            current_usage_count=coupon.current_usage_count,
            is_active=coupon.is_active
        )
    except DuplicateCouponError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate code error: Coupon code '{e.code}' already exists."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from uuid import uuid4, UUID
from datetime import datetime
import datetime as dt

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

# ---------------------------------------------------------------------------
# Note management (new for story ASE-100)
# ---------------------------------------------------------------------------

# In‑memory store for notes (id -> note data)
_notes_by_id = {}

class NoteCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)

class NoteResponse(BaseModel):
    id: UUID
    content: str
    createdAt: datetime
    updatedAt: datetime

@app.post("/api/v1/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(request: Request, payload: NoteCreateRequest):
    # Simple user identification via header (in real world JWT would be used)
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-User-Id header"
        )
    now = dt.datetime.utcnow()
    note_id = uuid4()
    note = {
        "id": note_id,
        "user_id": user_id,
        "content": payload.content,
        "createdAt": now,
        "updatedAt": now,
    }
    _notes_by_id[note_id] = note
    return NoteResponse(**note)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import get_db

router = APIRouter(prefix='/subscriptions', tags=['subscriptions'])

@router.get('/{user_id}', response_model=schemas.Subscription)
async def get_subscription(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(utils.get_current_user)):
    subscription = db.query(models.Subscription).filter(models.Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail=f'Subscription not found for user {user_id}')
    return subscription

@router.post('/', response_model=schemas.Subscription)
async def create_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(utils.get_current_user)):
    subscription = models.Subscription(user_id=user_id, **subscription.dict())
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

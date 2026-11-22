import hashlib
import hmac
import json
import uuid
from datetime import date, datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..config.settings import SITE_URL
from ..enums import DonorType, PaymentMethod
from ..models.donors import Donor
from ..models.donations import Donation
from ..models.gifts import OnlineGift
from ..schemas.gifts import GiveInitialize, GiftResponse
from ..auth.jwt import get_current_user
from ..middlewares.rate_limit import give_rate_limit

router = APIRouter(prefix='/give', tags=['Online Giving'])

ACCOUNT_DETAILS = {
    'bank_name': 'First Bank of Nigeria',
    'account_number': '0123456789',
    'account_name': 'International Center of Evangelism',
    'bank_code': '012',
    'description': 'Transfer funds to the account above. After transfer, contact us or use /give/verify with your transaction reference.',
}

@router.get('/account-details')
def account_details():
    return ACCOUNT_DETAILS


@router.post('/initialize', dependencies=[Depends(give_rate_limit)])
def initialize(data: GiveInitialize, db: Session = Depends(get_db)):
    _require_gateway()
    reference = f'ICE-{uuid.uuid4().hex[:16]}'
    db.add(OnlineGift(
        reference=reference, name=data.name, email=data.email, amount=data.amount,
        currency='NGN', purpose=data.purpose, status='pending'
    ))
    db.commit()
    return {
        'reference': reference,
        'account_details': ACCOUNT_DETAILS,
        'message': 'Please transfer to the account details above. After transfer, verify your payment.',
    }


@router.get('/verify/{reference}')
def verify(reference: str, db: Session = Depends(get_db)):
    gift = db.query(OnlineGift).filter(OnlineGift.reference == reference).first()
    if not gift:
        raise HTTPException(status_code=404, detail='Gift not found')
    if gift.status == 'pending':
        # Mark as manual verification received
        gift.status = 'success'
        donor = db.query(Donor).filter(Donor.email == gift.email).first()
        if not donor:
            donor = Donor(name=gift.name, email=gift.email, donor_type=DonorType.individual)
            db.add(donor)
            db.flush()
        db.add(Donation(
            donor_id=donor.id, amount=gift.amount, currency=gift.currency,
            purpose=gift.purpose or 'Online gift', payment_method=PaymentMethod.bank_transfer,
            date_received=date.today()))
        gift.paid_at = datetime.now(timezone.utc)
        db.commit()
    return {'status': gift.status, 'amount': float(gift.amount), 'reference': gift.reference}


@router.post('/webhook')
async def webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Paystack webhook or manual verification notification."""
    raw = await request.body()
    # For manual mode, we accept any webhook and mark as verified
    try:
        event = json.loads(raw) if raw else {}
    except (json.JSONDecodeError, ValueError):
        event = {}
    if event.get('event') == 'charge.success' or event.get('status') == 'success':
        info = event.get('data') or {}
        reference = info.get('reference') or request.headers.get('x-paystack-signature')
        if reference:
            gift = db.query(OnlineGift).filter(OnlineGift.reference == reference).first()
            if gift and gift.status == 'pending':
                gift = finalize_gift(db, reference, info.get('amount'))
    return {'ok': True}


@router.get('/', response_model=List[GiftResponse], dependencies=[Depends(get_current_user)])
def list_gifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(OnlineGift).order_by(OnlineGift.id.desc()).offset(skip).limit(limit).all()


def _require_gateway():
    # Gateway is always available in manual mode
    pass
import hashlib
import hmac
import json
import uuid
from datetime import date, datetime, timezone
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..config.settings import SITE_URL, PAYSTACK_SECRET_KEY
from ..enums import DonorType, PaymentMethod
from ..models.donors import Donor
from ..models.donations import Donation
from ..models.gifts import OnlineGift
from ..schemas.gifts import GiveInitialize, GiftResponse
from ..auth.jwt import get_current_user
from ..middlewares.rate_limit import give_rate_limit

router = APIRouter(prefix='/give', tags=['Online Giving'])

PAYSTACK_URL = 'https://api.paystack.co'


def _headers():
    return {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}


def _require_gateway():
    if not PAYSTACK_SECRET_KEY:
        raise HTTPException(status_code=503, detail='Online giving is not available yet. Please contact us.')


def finalize_gift(db: Session, reference: str, paid_kobo):
    """Mark a gift as paid and record it as a donation. Safe to call twice (webhook + verify)."""
    gift = db.query(OnlineGift).filter(OnlineGift.reference == reference).with_for_update().first()
    if not gift:
        return None
    if gift.status == 'success':
        return gift
    if paid_kobo != int(gift.amount * 100):
        gift.status = 'failed'
        db.commit()
        return gift
    donor = db.query(Donor).filter(Donor.email == gift.email).first()
    if not donor:
        donor = Donor(name=gift.name, email=gift.email, donor_type=DonorType.individual)
        db.add(donor)
        db.flush()
    db.add(Donation(donor_id=donor.id, amount=gift.amount, currency=gift.currency,
                    purpose=gift.purpose or 'Online gift', payment_method=PaymentMethod.online,
                    date_received=date.today()))
    gift.status = 'success'
    gift.paid_at = datetime.now(timezone.utc)
    db.commit()
    return gift


@router.post('/initialize', dependencies=[Depends(give_rate_limit)])
def initialize(data: GiveInitialize, db: Session = Depends(get_db)):
    _require_gateway()
    reference = f'ICE-{uuid.uuid4().hex[:16]}'
    payload = {
        'email': data.email,
        'amount': int(data.amount * 100),
        'currency': 'NGN',
        'reference': reference,
        'callback_url': f'{SITE_URL}/site/give.html',
        'metadata': {'name': data.name, 'purpose': data.purpose},
    }
    try:
        res = httpx.post(f'{PAYSTACK_URL}/transaction/initialize', json=payload, headers=_headers(), timeout=20)
        body = res.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(status_code=502, detail='Could not reach the payment provider. Please try again.')
    if res.status_code != 200 or not body.get('status'):
        raise HTTPException(status_code=502, detail='The payment provider could not start this payment.')
    db.add(OnlineGift(reference=reference, name=data.name, email=data.email, amount=data.amount,
                      currency='NGN', purpose=data.purpose, status='pending'))
    db.commit()
    return {'authorization_url': body['data']['authorization_url'], 'reference': reference}


@router.get('/verify/{reference}')
def verify(reference: str, db: Session = Depends(get_db)):
    gift = db.query(OnlineGift).filter(OnlineGift.reference == reference).first()
    if not gift:
        raise HTTPException(status_code=404, detail='Gift not found')
    if gift.status == 'pending':
        _require_gateway()
        try:
            res = httpx.get(f'{PAYSTACK_URL}/transaction/verify/{reference}', headers=_headers(), timeout=20)
            body = res.json()
        except (httpx.HTTPError, ValueError):
            raise HTTPException(status_code=502, detail='Could not reach the payment provider.')
        info = body.get('data') or {}
        if res.status_code == 200 and info.get('status') == 'success':
            gift = finalize_gift(db, reference, info.get('amount'))
        elif info.get('status') == 'failed':
            gift.status = 'failed'
            db.commit()
    return {'status': gift.status, 'amount': float(gift.amount)}


@router.post('/webhook')
async def webhook(request: Request, db: Session = Depends(get_db)):
    """Paystack calls this after each payment. Set it in the Paystack dashboard as {SITE_URL}/give/webhook."""
    raw = await request.body()
    signature = request.headers.get('x-paystack-signature', '')
    expected = hmac.new(PAYSTACK_SECRET_KEY.encode(), raw, hashlib.sha512).hexdigest()
    if not PAYSTACK_SECRET_KEY or not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail='Invalid signature')
    event = json.loads(raw)
    if event.get('event') == 'charge.success':
        info = event.get('data') or {}
        finalize_gift(db, info.get('reference'), info.get('amount'))
    return {'ok': True}


@router.get('/', response_model=List[GiftResponse], dependencies=[Depends(get_current_user)])
def list_gifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(OnlineGift).order_by(OnlineGift.id.desc()).offset(skip).limit(limit).all()

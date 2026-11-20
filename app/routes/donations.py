from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.donors import Donor
from ..models.donations import Donation
from ..schemas.donations import DonationCreate, DonationResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/donations', tags=['Donations'], dependencies=[Depends(get_current_user)])


@router.post('/', response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def record_donation(data: DonationCreate, db: Session = Depends(get_db)):
    if not db.query(Donor).filter(Donor.id == data.donor_id).first():
        raise HTTPException(status_code=404, detail='Donor not found')
    donation = Donation(**data.model_dump())
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


@router.get('/', response_model=List[DonationResponse])
def list_donations(donor_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Donation)
    if donor_id:
        query = query.filter(Donation.donor_id == donor_id)
    return query.order_by(Donation.date_received.desc()).offset(skip).limit(limit).all()


@router.get('/summary')
def summary(db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(Donation.amount), 0)).scalar()
    return {
        'total_donations': float(total),
        'donation_count': db.query(Donation).count(),
        'donor_count': db.query(Donor).count(),
    }


@router.delete('/{donation_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_donation(donation_id: int, db: Session = Depends(get_db)):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found')
    db.delete(donation)
    db.commit()

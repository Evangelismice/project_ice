from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..enums import DonorType
from ..models.donors import Donor
from ..schemas.donors import DonorCreate, DonorUpdate, DonorResponse
from ..schemas.donations import DonationResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/donors', tags=['Donors'], dependencies=[Depends(get_current_user)])


@router.post('/', response_model=DonorResponse, status_code=status.HTTP_201_CREATED)
def create_donor(data: DonorCreate, db: Session = Depends(get_db)):
    donor = Donor(**data.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.get('/', response_model=List[DonorResponse])
def list_donors(
    q: Optional[str] = None,
    donor_type: Optional[DonorType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Donor)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Donor.name.ilike(like), Donor.email.ilike(like), Donor.phone.ilike(like)))
    if donor_type:
        query = query.filter(Donor.donor_type == donor_type)
    return query.order_by(Donor.name).offset(skip).limit(limit).all()


@router.get('/{donor_id}', response_model=DonorResponse)
def get_donor(donor_id: int, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail='Donor not found')
    return donor


@router.get('/{donor_id}/donations', response_model=List[DonationResponse])
def donor_donations(donor_id: int, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail='Donor not found')
    return donor.donations


@router.put('/{donor_id}', response_model=DonorResponse)
def update_donor(donor_id: int, data: DonorUpdate, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail='Donor not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(donor, key, value)
    db.commit()
    db.refresh(donor)
    return donor


@router.delete('/{donor_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_donor(donor_id: int, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail='Donor not found')
    db.delete(donor)
    db.commit()

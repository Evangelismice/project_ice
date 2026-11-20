from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..enums import Department, StaffStatus
from ..models.staffs import Staff
from ..schemas.staffs import StaffCreate, StaffUpdate, StaffResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/staffs', tags=['Staffs'], dependencies=[Depends(get_current_user)])


@router.post('/', response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(data: StaffCreate, db: Session = Depends(get_db)):
    if data.email and db.query(Staff).filter(Staff.email == data.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')
    staff = Staff(**data.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.get('/', response_model=List[StaffResponse])
def list_staffs(
    q: Optional[str] = None,
    department: Optional[Department] = None,
    status: Optional[StaffStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Staff)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Staff.first_name.ilike(like), Staff.last_name.ilike(like),
                                 Staff.email.ilike(like), Staff.phone.ilike(like)))
    if department:
        query = query.filter(Staff.department == department)
    if status:
        query = query.filter(Staff.status == status)
    return query.order_by(Staff.last_name).offset(skip).limit(limit).all()


@router.get('/{staff_id}', response_model=StaffResponse)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail='Staff not found')
    return staff


@router.put('/{staff_id}', response_model=StaffResponse)
def update_staff(staff_id: int, data: StaffUpdate, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail='Staff not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


@router.delete('/{staff_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail='Staff not found')
    db.delete(staff)
    db.commit()

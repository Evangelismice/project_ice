from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..enums import MemberType
from ..models.members import Member
from ..schemas.members import MemberCreate, MemberUpdate, MemberResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/members', tags=['Members'], dependencies=[Depends(get_current_user)])


@router.post('/', response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    member = Member(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get('/', response_model=List[MemberResponse])
def list_members(q: Optional[str] = None, member_type: Optional[MemberType] = None, skip: int = 0,
                 limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Member)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Member.name.ilike(like), Member.email.ilike(like), Member.phone.ilike(like)))
    if member_type:
        query = query.filter(Member.member_type == member_type)
    return query.order_by(Member.name).offset(skip).limit(limit).all()


@router.put('/{member_id}', response_model=MemberResponse)
def update_member(member_id: int, data: MemberUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail='Member not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member


@router.delete('/{member_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail='Member not found')
    db.delete(member)
    db.commit()

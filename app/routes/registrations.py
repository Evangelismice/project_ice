from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.events import Event
from ..models.registrations import Registration
from ..schemas.registrations import RegistrationCreate, RegistrationResponse
from ..auth.jwt import get_current_user
from ..middlewares.rate_limit import form_rate_limit

router = APIRouter(prefix='/registrations', tags=['Registrations'])


@router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(form_rate_limit)])
def register(data: RegistrationCreate, db: Session = Depends(get_db)):
    """Public: event registration form."""
    if data.website:  # honeypot
        return {'message': 'Thank you'}
    event = db.query(Event).filter(Event.id == data.event_id, Event.is_published == True).first()  # noqa: E712
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    db.add(Registration(**data.model_dump(exclude={'website'})))
    db.commit()
    return {'message': 'Thank you'}


@router.get('/', response_model=List[RegistrationResponse], dependencies=[Depends(get_current_user)])
def list_registrations(q: Optional[str] = None, event_id: Optional[int] = None, skip: int = 0,
                       limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Registration)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Registration.name.ilike(like), Registration.email.ilike(like),
                                 Registration.church.ilike(like)))
    if event_id:
        query = query.filter(Registration.event_id == event_id)
    return query.order_by(Registration.id.desc()).offset(skip).limit(limit).all()


@router.delete('/{registration_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_registration(registration_id: int, db: Session = Depends(get_db)):
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail='Registration not found')
    db.delete(reg)
    db.commit()

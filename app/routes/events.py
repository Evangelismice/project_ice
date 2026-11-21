from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.events import Event
from ..schemas.events import EventCreate, EventUpdate, EventResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/events', tags=['Events'], dependencies=[Depends(get_current_user)])
public_router = APIRouter(prefix='/public', tags=['Public'])


@router.post('/', response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get('/', response_model=List[EventResponse])
def list_events(q: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Event)
    if q:
        query = query.filter(Event.title.ilike(f'%{q}%'))
    return query.order_by(Event.event_date.desc()).offset(skip).limit(limit).all()


@router.put('/{event_id}', response_model=EventResponse)
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete('/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    db.delete(event)
    db.commit()


@public_router.get('/events', response_model=List[EventResponse])
def upcoming_events(limit: int = 12, db: Session = Depends(get_db)):
    """Public list for the website: upcoming events only."""
    return (db.query(Event).filter(Event.event_date >= date.today())
            .order_by(Event.event_date).limit(limit).all())
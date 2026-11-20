from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.events import Event
from ..schemas.events import EventCreate, EventUpdate, EventResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/events', tags=['Events'])


@router.get('/', response_model=List[EventResponse])
def upcoming_events(db: Session = Depends(get_db)):
    """Public: published events from today onwards."""
    return (db.query(Event).filter(Event.is_published == True, Event.event_date >= date.today())  # noqa: E712
            .order_by(Event.event_date).all())


@router.get('/manage', response_model=List[EventResponse], dependencies=[Depends(get_current_user)])
def all_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date.desc()).all()


@router.post('/', response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_user)])
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.put('/{event_id}', response_model=EventResponse, dependencies=[Depends(get_current_user)])
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete('/{event_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    db.delete(event)
    db.commit()

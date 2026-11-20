from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.messages import ContactMessage
from ..schemas.messages import ContactCreate, ContactResponse
from ..auth.jwt import get_current_user
from ..middlewares.rate_limit import contact_rate_limit

router = APIRouter(prefix='/contact', tags=['Contact'])


@router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(contact_rate_limit)])
def submit_message(data: ContactCreate, db: Session = Depends(get_db)):
    """Public endpoint used by the website contact form."""
    if data.website:  # bots fill the hidden field; pretend success and drop it
        return {'message': 'Thank you'}
    db.add(ContactMessage(**data.model_dump(exclude={'website'})))
    db.commit()
    return {'message': 'Thank you'}


@router.get('/', response_model=List[ContactResponse], dependencies=[Depends(get_current_user)])
def list_messages(
    q: Optional[str] = None,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(ContactMessage)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(ContactMessage.name.ilike(like), ContactMessage.email.ilike(like),
                                 ContactMessage.subject.ilike(like)))
    if is_read is not None:
        query = query.filter(ContactMessage.is_read == is_read)
    return query.order_by(ContactMessage.id.desc()).offset(skip).limit(limit).all()


@router.patch('/{message_id}/read', response_model=ContactResponse, dependencies=[Depends(get_current_user)])
def mark_read(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail='Message not found')
    msg.is_read = True
    db.commit()
    db.refresh(msg)
    return msg


@router.delete('/{message_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail='Message not found')
    db.delete(msg)
    db.commit()

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..config.settings import UPLOAD_DIR
from ..models.gallery import GalleryItem
from ..schemas.gallery import GalleryResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/gallery', tags=['Gallery'])

MAX_BYTES = 5 * 1024 * 1024


def detect_extension(data: bytes):
    """Check the real file signature instead of trusting the browser's content type."""
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return '.webp'
    return None


@router.get('/', response_model=List[GalleryResponse])
def list_gallery(db: Session = Depends(get_db)):
    return db.query(GalleryItem).order_by(GalleryItem.id.desc()).all()


@router.post('/', response_model=GalleryResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_user)])
async def upload_photo(title: str = Form(...), caption: Optional[str] = Form(None),
                       file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail='Image must be 5MB or smaller')
    ext = detect_extension(data)
    if not ext:
        raise HTTPException(status_code=400, detail='Only JPG, PNG or WEBP images are allowed')
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f'{uuid.uuid4().hex}{ext}'
    with open(os.path.join(UPLOAD_DIR, filename), 'wb') as out:
        out.write(data)
    item = GalleryItem(title=title[:150], caption=caption[:255] if caption else None, filename=filename)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
def delete_photo(item_id: int, db: Session = Depends(get_db)):
    item = db.query(GalleryItem).filter(GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Photo not found')
    path = os.path.join(UPLOAD_DIR, item.filename)
    db.delete(item)
    db.commit()
    if os.path.exists(path):
        os.remove(path)

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.gallery import GalleryImage
from ..schemas.gallery import GalleryCreate, GalleryUpdate, GalleryResponse
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/gallery', tags=['Gallery'], dependencies=[Depends(get_current_user)])
public_router = APIRouter(prefix='/public', tags=['Public'])


@router.post('/', response_model=GalleryResponse, status_code=status.HTTP_201_CREATED)
def add_image(data: GalleryCreate, db: Session = Depends(get_db)):
    image = GalleryImage(**data.model_dump())
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.get('/', response_model=List[GalleryResponse])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(GalleryImage).order_by(GalleryImage.id.desc()).offset(skip).limit(limit).all()


@router.put('/{image_id}', response_model=GalleryResponse)
def update_image(image_id: int, data: GalleryUpdate, db: Session = Depends(get_db)):
    image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail='Photo not found')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(image, key, value)
    db.commit()
    db.refresh(image)
    return image


@router.delete('/{image_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail='Photo not found')
    db.delete(image)
    db.commit()


@public_router.get('/gallery', response_model=List[GalleryResponse])
def public_gallery(skip: int = 0, limit: int = 12, db: Session = Depends(get_db)):
    """Public list for the website, newest first."""
    limit = min(limit, 50)
    return db.query(GalleryImage).order_by(GalleryImage.id.desc()).offset(skip).limit(limit).all()
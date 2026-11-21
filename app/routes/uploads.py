import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import cloudinary.uploader

from ..auth.jwt import get_current_user
from ..config.media import cloudinary_ready

router = APIRouter(prefix='/uploads', tags=['Uploads'], dependencies=[Depends(get_current_user)])

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_BYTES = 5 * 1024 * 1024


@router.post('/')
def upload_image(file: UploadFile = File(...)):
    if not cloudinary_ready():
        raise HTTPException(status_code=503, detail='Image uploads are not set up yet. Add the Cloudinary keys to .env')
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG or WebP images are allowed')
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail='Image must be 5 MB or smaller')
    try:
        result = cloudinary.uploader.upload(io.BytesIO(data), folder='ice', resource_type='image')
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'Image upload failed: {exc}')
    return {'url': result['secure_url']}
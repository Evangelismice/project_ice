import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import cloudinary.uploader

from ..auth.jwt import get_current_user
from ..config.media import cloudinary_ready

router = APIRouter(prefix='/uploads', tags=['Uploads'], dependencies=[Depends(get_current_user)])

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_VIDEO_TYPES = {'video/mp4', 'video/quicktime', 'video/x-msvideo'}
MAX_BYTES = 50 * 1024 * 1024  # 50 MB for videos


@router.post('/')
def upload_image(file: UploadFile = File(...)):
    if not cloudinary_ready():
        raise HTTPException(status_code=503, detail='Image uploads are not set up yet. Add the Cloudinary keys to .env')
    if file.content_type in ALLOWED_IMAGE_TYPES:
        resource_type = 'image'
        allowed_types = ALLOWED_IMAGE_TYPES
    elif file.content_type in ALLOWED_VIDEO_TYPES:
        resource_type = 'video'
        allowed_types = ALLOWED_VIDEO_TYPES
    else:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG, WebP images or MP4 videos are allowed')
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail='File must be 50 MB or smaller')
    try:
        result = cloudinary.uploader.upload(io.BytesIO(data), folder='ice', resource_type=resource_type)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'Upload failed: {exc}')
    return {'url': result['secure_url'], 'resource_type': resource_type}
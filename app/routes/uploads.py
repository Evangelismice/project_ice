import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import cloudinary.uploader

from ..auth.jwt import get_current_user
from ..config.media import cloudinary_ready

router = APIRouter(prefix='/uploads', tags=['Uploads'], dependencies=[Depends(get_current_user)])

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_VIDEO_TYPES = {'video/mp4', 'video/webm', 'video/quicktime'}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_VIDEO_BYTES = 100 * 1024 * 1024


def _upload_error(exc):
    raise HTTPException(status_code=502, detail=f'Media upload failed: {exc}')


@router.post('/')
def upload_media(file: UploadFile = File(...)):
    if not cloudinary_ready():
        raise HTTPException(status_code=503, detail='Media uploads are not set up yet. Add the Cloudinary keys to .env')
    is_video = file.content_type in ALLOWED_VIDEO_TYPES
    if not is_video and file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG, WebP, MP4, WebM or MOV files are allowed')

    max_bytes = MAX_VIDEO_BYTES if is_video else MAX_IMAGE_BYTES
    data = file.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        limit = '100 MB' if is_video else '5 MB'
        raise HTTPException(status_code=400, detail=f'Media must be {limit} or smaller')
    try:
        resource_type = 'video' if is_video else 'image'
        result = cloudinary.uploader.upload(
            io.BytesIO(data), folder='ice', resource_type=resource_type
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'Media upload failed: {exc}')
    return {'url': result['secure_url'], 'media_type': 'video' if is_video else 'image'}
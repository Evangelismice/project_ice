import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models.base import Base
from . import models  # noqa: F401  (registers all models)
from .routes.auth import router as auth_routes
from .routes.staffs import router as staff_routes
from .routes.donors import router as donor_routes
from .routes.donations import router as donation_routes
from .routes.messages import router as message_routes
from .routes.events import router as event_routes, public_router as public_event_routes
from .routes.gallery import router as gallery_routes, public_router as public_gallery_routes
from .routes.uploads import router as upload_routes
from .routes.giving import router as giving_routes



Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='ICE Management System',
    version='2.1.0',
    description='Public website and staff/donor management for the International Center of Evangelism, Jos.',
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

app.include_router(auth_routes)
app.include_router(staff_routes)
app.include_router(donor_routes)
app.include_router(donation_routes)
app.include_router(message_routes)
app.include_router(event_routes)
app.include_router(public_event_routes)
app.include_router(gallery_routes)
app.include_router(public_gallery_routes)
app.include_router(upload_routes)
app.include_router(giving_routes)

app.mount('/site', StaticFiles(directory=os.path.join(STATIC_DIR, 'site'), html=True), name='site')
app.mount('/admin', StaticFiles(directory=os.path.join(STATIC_DIR, 'admin'), html=True), name='admin')


@app.get('/', include_in_schema=False)
def index():
    return RedirectResponse('/site/')
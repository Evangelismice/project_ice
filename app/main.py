import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models.base import Base
from . import models  # noqa: F401  (registers all models)
from .config.settings import STATIC_DIR, UPLOAD_DIR
from .routes.auth import router as auth_routes
from .routes.staffs import router as staff_routes
from .routes.donors import router as donor_routes
from .routes.donations import router as donation_routes
from .routes.messages import router as message_routes
from .routes.members import router as member_routes
from .routes.events import router as event_routes
from .routes.registrations import router as registration_routes
from .routes.gallery import router as gallery_routes
from .routes.giving import router as giving_routes
from .routes.reports import router as report_routes

Base.metadata.create_all(bind=engine)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title='ICE Management System',
    version='3.0.0',
    description='Website, online giving and management system for the International Center of Evangelism, Jos.',
)

app.include_router(auth_routes)
app.include_router(staff_routes)
app.include_router(member_routes)
app.include_router(donor_routes)
app.include_router(donation_routes)
app.include_router(giving_routes)
app.include_router(event_routes)
app.include_router(registration_routes)
app.include_router(gallery_routes)
app.include_router(message_routes)
app.include_router(report_routes)

app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR), name='uploads')
app.mount('/site', StaticFiles(directory=os.path.join(STATIC_DIR, 'site'), html=True), name='site')
app.mount('/admin', StaticFiles(directory=os.path.join(STATIC_DIR, 'admin'), html=True), name='admin')


@app.get('/', include_in_schema=False)
def index():
    return RedirectResponse('/site/')

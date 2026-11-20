from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.users import User
from ..schemas.auth import UserCreate, Token
from ..auth.jwt import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """The first admin can register freely; after that only a logged-in admin can add users."""
    if db.query(User).count() > 0:
        raise HTTPException(status_code=403, detail='Use /auth/add-user while logged in')
    user = User(username=data.username, password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {'message': 'Admin created'}


@router.post('/add-user', status_code=status.HTTP_201_CREATED)
def add_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail='Username already exists')
    db.add(User(username=data.username, password=hash_password(data.password)))
    db.commit()
    return {'message': 'User created'}


@router.post('/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    return Token(access_token=create_access_token(user.username))

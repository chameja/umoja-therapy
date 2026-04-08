from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from models import User, UserRole, Client, Therapist
from schemas import ClientRegister, TherapistRegister
from security import verify_password, create_access_token, get_password_hash

router = APIRouter(tags=["Authentication"])

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.user_id), "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/client", status_code=status.HTTP_201_CREATED)
def register_client(new_client_data: ClientRegister, db: Session = Depends(get_session)):
    existing_user = db.exec(select(User).where(User.email == new_client_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=new_client_data.email,
        hashed_password=get_password_hash(new_client_data.password),
        role=UserRole.client
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_client_profile = Client(
        client_name=new_client_data.client_name,
        user_id=new_user.user_id
    )
    db.add(new_client_profile)
    db.commit()
    db.refresh(new_client_profile)

    return {"message": "Client registered successfully", "client_profile": new_client_profile}

@router.post("/register/therapist", status_code=status.HTTP_201_CREATED)
def register_therapist(new_therapist_data: TherapistRegister, db: Session = Depends(get_session)):
    existing_user = db.exec(select(User).where(User.email == new_therapist_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=new_therapist_data.email,
        hashed_password=get_password_hash(new_therapist_data.password),
        role=UserRole.therapist
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_therapist_profile = Therapist(
        therapist_name=new_therapist_data.therapist_name,
        user_id=new_user.user_id
    )
    db.add(new_therapist_profile)
    db.commit()
    db.refresh(new_therapist_profile)

    return {"message": "Therapist registered successfully", "therapist_profile": new_therapist_profile}


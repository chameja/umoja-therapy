from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from database import get_session
from dependencies import get_current_user
from models import User, UserRole, Client, Therapist

router = APIRouter(tags=["Users and Profiles"])

@router.get("/users/me", tags=["Users"])
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Find the specific profile linked to this user account
    if current_user.role == UserRole.client:
        profile = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
        name = profile.client_name if profile else "Unknown Client"
    elif current_user.role == UserRole.therapist:
        profile = db.exec(select(Therapist).where(Therapist.user_id == current_user.user_id)).first()
        name = profile.therapist_name if profile else "Unknown Therapist"
    else:
        name = "Admin"
        
    return {
        "email": current_user.email,
        "role": current_user.role,
        "name": name
    }

@router.get("/clients/", response_model=List[Client], tags=["Clients"])
def get_clients(
    db: Session = Depends(get_session),
):
    clients = db.exec(select(Client)).all()
    return clients

@router.put("/clients/{client_id}", response_model=Client, tags=["Clients"])
def edit_client(client_id: int, updated_client: Client, db: Session = Depends(get_session)):
    client_to_update = db.get(Client, client_id)
    if not client_to_update:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_data = updated_client.model_dump(exclude_unset=True)
    for key, value in client_data.items():
        setattr(client_to_update, key, value)
        
    db.add(client_to_update)
    db.commit()
    db.refresh(client_to_update)
    return client_to_update

@router.get("/therapists/", response_model=List[Therapist], tags=["Therapists"])
def get_therapists(db: Session = Depends(get_session)):
    return db.exec(select(Therapist)).all()

@router.get("/therapists/", tags=["Directory"])
def get_all_therapists(db: Session = Depends(get_session)):
    return db.exec(select(Therapist)).all()

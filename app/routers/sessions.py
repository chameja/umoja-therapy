from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from dependencies import get_current_user
from models import (User, UserRole, Client, Therapist, SessionRequest, 
                    SessionStatus, ClientAssignment, TherapySession, IntakeFormQuestion)
from schemas import SessionRequestCreate, SessionRequestUpdate, SessionNotesUpdate

router = APIRouter(tags=["Sessions and Virtual Rooms"])

@router.post("/session-requests", status_code=status.HTTP_201_CREATED, tags=["Sessions"])
def create_session_request(request_data: SessionRequestCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user.role != UserRole.client:
        raise HTTPException(status_code=403, detail="Only clients can request sessions.")
        
    client = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
    
    new_request = SessionRequest(
        client_id=client.client_id,
        therapist_id=request_data.therapist_id,
        start_time=request_data.start_time,
        end_time=request_data.end_time,
        status=SessionStatus.open
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("/session-requests/me", tags=["Sessions"])
def get_my_session_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    enriched_requests = []
    
    # If the user is a Client
    if current_user.role == UserRole.client:
        client = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
        requests = db.exec(select(SessionRequest).where(SessionRequest.client_id == client.client_id)).all()
        
        for req in requests:
            enriched_requests.append(req.model_dump())
            
    # If the user is a Therapist
    elif current_user.role == UserRole.therapist:
        therapist = db.exec(select(Therapist).where(Therapist.user_id == current_user.user_id)).first()
        requests = db.exec(select(SessionRequest).where(SessionRequest.therapist_id == therapist.therapist_id)).all()
        
        for req in requests:
            intake_records = db.exec(select(IntakeFormQuestion).where(IntakeFormQuestion.client_id == req.client_id)).all()
            
            intake_dict = {item.question_text: item.response for item in intake_records} if intake_records else None            
            req_data = req.model_dump()
            req_data["intake_answers"] = intake_dict 
            
            enriched_requests.append(req_data)
            
    return enriched_requests

@router.patch("/session-requests/{request_id}/status", tags=["Sessions"])
def update_session_request_status(request_id: int, status_update: SessionRequestUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user.role != UserRole.therapist:
        raise HTTPException(status_code=403, detail="Only therapists can approve or decline requests.")
        
    therapist = db.exec(select(Therapist).where(Therapist.user_id == current_user.user_id)).first()
    session_req = db.get(SessionRequest, request_id)
    
    if not session_req or session_req.therapist_id != therapist.therapist_id:
        raise HTTPException(status_code=404, detail="Session request not found or unauthorized.")
        
    session_req.status = status_update.status
    db.add(session_req)
    
    if status_update.status == SessionStatus.accepted:
        assignment = db.exec(select(ClientAssignment).where(
            ClientAssignment.client_id == session_req.client_id,
            ClientAssignment.therapist_id == therapist.therapist_id
        )).first()
        
        if not assignment:
            new_assignment = ClientAssignment(client_id=session_req.client_id, therapist_id=therapist.therapist_id)
            db.add(new_assignment)
            
        duration_minutes = int((session_req.end_time - session_req.start_time).total_seconds() / 60)
        new_session = TherapySession(
            session_request_id=session_req.session_request_id,
            client_id=session_req.client_id,
            therapist_id=therapist.therapist_id,
            start_time=session_req.start_time,
            end_time=session_req.end_time,
            duration=duration_minutes
        )
        db.add(new_session)

    db.commit()
    return {"message": f"Session request {status_update.status.name}."}

@router.get("/sessions/{session_id}", tags=["Virtual Room"])
def get_session_room(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # 1. Get the session
    therapy_session = db.exec(select(TherapySession).where(TherapySession.session_request_id == session_id)).first()
    if not therapy_session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # 2. Determine who is asking and verify they belong in this session
    is_authorized = False
    participant_name = ""
    other_person_name = ""

    if current_user.role == UserRole.client:
        client = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
        if client and therapy_session.client_id == client.client_id:
            is_authorized = True
            participant_name = client.client_name
            therapist = db.get(Therapist, therapy_session.therapist_id)
            other_person_name = therapist.therapist_name if therapist else "Therapist"

    elif current_user.role == UserRole.therapist:
        therapist = db.exec(select(Therapist).where(Therapist.user_id == current_user.user_id)).first()
        if therapist and therapy_session.therapist_id == therapist.therapist_id:
            is_authorized = True
            participant_name = therapist.therapist_name
            client = db.get(Client, therapy_session.client_id)
            other_person_name = client.client_name if client else "Client"

    if not is_authorized:
        raise HTTPException(status_code=403, detail="You do not have access to this session room.")

    return {
        "session_id": therapy_session.session_id,
        "start_time": therapy_session.start_time,
        "duration": therapy_session.duration,
        "notes": therapy_session.session_notes,
        "my_name": participant_name,
        "partner_name": other_person_name,
        "video_room_id": f"UmojaTherapy_Room_{therapy_session.session_id}_{therapy_session.client_id}"
    }

@router.put("/sessions/{session_id}/notes", tags=["Virtual Room"])
def save_session_notes(session_id: int, data: SessionNotesUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user.role != UserRole.therapist:
        raise HTTPException(status_code=403, detail="Only therapists can save session notes.")
        
    therapist = db.exec(select(Therapist).where(Therapist.user_id == current_user.user_id)).first()
    therapy_session = db.exec(select(TherapySession).where(TherapySession.session_request_id == session_id)).first()
    
    if not therapy_session or therapy_session.therapist_id != therapist.therapist_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to these notes.")
        
    therapy_session.session_notes = data.notes
    db.add(therapy_session)
    db.commit()
    
    return {"message": "Notes saved securely."}

@router.post("/session-requests/", response_model=SessionRequest, tags=["Session Requests"])
def add_session_request(request: SessionRequest, db: Session = Depends(get_session)):
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

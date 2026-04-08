from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from dependencies import get_current_user
from models import User, UserRole, Client, IntakeFormQuestion
from schemas import IntakeUpdate

router = APIRouter(prefix="/my-intake", tags=["Client Portal"])

@router.get("/")
def get_my_intake(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user.role != UserRole.client:
        raise HTTPException(status_code=403, detail="Only clients can access this.")
    
    client = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
    
    # Fetch all existing questions/responses for this client
    questions = db.exec(select(IntakeFormQuestion).where(IntakeFormQuestion.client_id == client.client_id)).all()
    
    if not questions:
        # Provide default questions for brand new clients
        default_questions = [
            "What brings you to therapy today?",
            "Have you attended therapy before?",
            "What are your goals for these sessions?"
        ]
        return {"answers": [{"question_text": q, "response": ""} for q in default_questions]}
        
    return {"answers": [
        {
            "intake_form_question_id": q.intake_form_question_id, 
            "question_text": q.question_text, 
            "response": q.response
        } for q in questions
    ]}

@router.put("/")
def update_my_intake(data: IntakeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    if current_user.role != UserRole.client:
        raise HTTPException(status_code=403, detail="Only clients can access this.")
        
    client = db.exec(select(Client).where(Client.user_id == current_user.user_id)).first()
    
    for item in data.answers:
        if item.intake_form_question_id:
            # Update existing answer
            record = db.get(IntakeFormQuestion, item.intake_form_question_id)
            if record and record.client_id == client.client_id:
                record.response = item.response
                db.add(record)
        else:
            # Create new answer record
            new_record = IntakeFormQuestion(
                client_id=client.client_id,
                question_text=item.question_text, 
                response=item.response
            )
            db.add(new_record)
            
    db.commit()
    return {"message": "Intake form updated successfully!"}

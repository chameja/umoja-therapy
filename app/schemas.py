from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import SessionStatus

class ClientRegister(BaseModel):
    email: EmailStr
    password: str
    client_name: str

class TherapistRegister(BaseModel):
    email: EmailStr
    password: str
    therapist_name: str

class QuestionResponse(BaseModel):
    intake_form_question_id: Optional[int] = None
    question_text: str
    response: str

class IntakeUpdate(BaseModel):
    answers: List[QuestionResponse]

class SessionRequestCreate(BaseModel):
    therapist_id: int
    start_time: datetime
    end_time: datetime

class SessionRequestUpdate(BaseModel):
    status: SessionStatus

class SessionNotesUpdate(BaseModel):
    notes: str

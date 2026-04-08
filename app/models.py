from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    open = "Open"
    accepted = "Accepted"
    declined = "Declined"
    expired = "Expired"
    cancelled = "Cancelled"

class UserRole(str, Enum):
    admin = "admin"
    therapist = "therapist"
    client = "client"
    
class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.client)
    is_active: bool = Field(default=True)

class Client(SQLModel, table=True):
    client_id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str
    user_id: int = Field(foreign_key="user.user_id")

class Therapist(SQLModel, table=True):
    therapist_id: Optional[int] = Field(default=None, primary_key=True)
    therapist_name: str
    user_id: int = Field(foreign_key="user.user_id")

class IntakeFormQuestion(SQLModel, table=True):
    intake_form_question_id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.client_id")
    response: str
    question_text: str

class ClientAssignment(SQLModel, table=True):
    client_assignment_id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.client_id")
    therapist_id: int = Field(foreign_key="therapist.therapist_id")

class SessionRequest(SQLModel, table=True):
    session_request_id: Optional[int] = Field(default=None, primary_key=True)
    therapist_id: int = Field(foreign_key="therapist.therapist_id")
    client_id: int = Field(foreign_key="client.client_id")
    start_time: datetime
    end_time: datetime
    status: SessionStatus

class TherapySession(SQLModel, table=True): 
    session_id: Optional[int] = Field(default=None, primary_key=True)
    session_request_id: int = Field(foreign_key="sessionrequest.session_request_id")
    therapist_id: int = Field(foreign_key="therapist.therapist_id")
    client_id: int = Field(foreign_key="client.client_id")
    start_time: datetime
    end_time: datetime
    duration: int
    session_notes: Optional[str] = None

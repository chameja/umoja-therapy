from sqlmodel import Session
from datetime import datetime, timedelta
from main import (
    engine, User, UserRole, Client, Therapist, 
    IntakeFormQuestion, ClientAssignment, 
    SessionRequest, TherapySession, SessionStatus
)
from security import get_password_hash

def seed_database():
    print("Starting database seed process...")
    
    with Session(engine) as session:
        # Pre-hash a common password for all test accounts to speed up seeding
        print("Hashing default password for test accounts...")
        default_password = get_password_hash("password123")

        # --- 1. Create Users (Admins, Therapists, Clients) ---
        print("Creating User accounts...")
        admins = [
            User(email=f"admin{i}@umoja.com", hashed_password=default_password, role=UserRole.admin) 
            for i in range(1, 6)
        ]
        therapist_users = [
            User(email=f"therapist{i}@umoja.com", hashed_password=default_password, role=UserRole.therapist) 
            for i in range(1, 6)
        ]
        client_users = [
            User(email=f"client{i}@umoja.com", hashed_password=default_password, role=UserRole.client) 
            for i in range(1, 6)
        ]
        
        # Add and commit all users to generate their user_ids
        all_users = admins + therapist_users + client_users
        session.add_all(all_users)
        session.commit()
        for user in all_users: 
            session.refresh(user)
        print("✅ Added 5 Admins, 5 Therapists, 5 Clients (Users Table)")

        # --- 2. Create Therapist Profiles ---
        therapist_names = [
            "Dr. Sarah Connor", "Dr. Hannibal Lecter", 
            "Dr. Harleen Quinzel", "Dr. Frasier Crane", "Dr. Jean Milburn"
        ]
        therapists = [
            Therapist(therapist_name=therapist_names[i], user_id=therapist_users[i].user_id) 
            for i in range(5)
        ]
        session.add_all(therapists)
        session.commit()
        for t in therapists: session.refresh(t)
        print("✅ Added 5 Therapist Profiles")

        # --- 3. Create Client Profiles ---
        client_names = [
            "Alice Johnson", "Bob Smith", 
            "Charlie Davis", "Diana Prince", "Ethan Hunt"
        ]
        clients = [
            Client(client_name=client_names[i], user_id=client_users[i].user_id) 
            for i in range(5)
        ]
        session.add_all(clients)
        session.commit()
        for c in clients: session.refresh(c)
        print("✅ Added 5 Client Profiles")

        # --- 4. Create Intake Form Questions & Responses ---
        # Giving each client a couple of seeded questions
        intake_questions = []
        for i, client in enumerate(clients):
            intake_questions.extend([
                IntakeFormQuestion(
                    client_id=client.client_id, 
                    question_text="What brings you to therapy today?", 
                    response=f"I am looking for help with stress management, specifically related to issue #{i+1}."
                ),
                IntakeFormQuestion(
                    client_id=client.client_id, 
                    question_text="Have you attended therapy before?", 
                    response="No, this is my first time seeking professional help."
                )
            ])
        
        session.add_all(intake_questions)
        session.commit()
        print("✅ Added Intake Form Questions & Responses")

        # --- 5. Create Matching Services ---
        matches = [
            ClientAssignment(
                client_id=clients[i].client_id,
                therapist_id=therapists[i].therapist_id
            )
            for i in range(5)
        ]
        session.add_all(matches)
        session.commit()
        print("✅ Added 5 Client Assignment Records")

        # --- 6. Create Session Requests ---
        now = datetime.now()
        session_requests = [
            SessionRequest(
                client_id=clients[i].client_id,
                therapist_id=therapists[i].therapist_id,
                start_time=now + timedelta(days=i + 1, hours=10), # Scheduled for upcoming days
                end_time=now + timedelta(days=i + 1, hours=11),
                status=SessionStatus.accepted
            )
            for i in range(5)
        ]
        session.add_all(session_requests)
        session.commit()
        for req in session_requests: session.refresh(req)
        print("✅ Added 5 Session Requests")

        # --- 7. Create Therapy Sessions ---
        therapy_sessions = [
            TherapySession(
                session_request_id=session_requests[i].session_request_id,
                client_id=clients[i].client_id,
                therapist_id=therapists[i].therapist_id,
                start_time=session_requests[i].start_time,
                end_time=session_requests[i].end_time,
                duration=60 # 60 minutes
            )
            for i in range(5)
        ]
        session.add_all(therapy_sessions)
        session.commit()
        print("✅ Added 5 Therapy Sessions")
        
        print("-" * 30)
        print("🎉 Database seeding complete!")
        print("You can log in using any of these emails with the password 'password123':")
        print(" - admin1@umoja.com")
        print(" - therapist1@umoja.com")
        print(" - client1@umoja.com")

if __name__ == "__main__":
    seed_database()
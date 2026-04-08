# 🌍 Umoja Therapy

Umoja Therapy is a secure, full-stack telehealth platform designed to bridge the mental health access gap in underserved areas. It provides a seamless digital environment connecting clients with qualified therapists through integrated scheduling, intake management, and secure real-time video sessions.

## ✨ Key Features

* **Role-Based Portals:** Dedicated, secure dashboards for Clients and Therapists.
* **Secure Authentication:** JWT-based user authentication and role authorization.
* **Session Management:** Clients can request sessions; Therapists can review, accept, or decline them.
* **Dynamic Intake Forms:** Therapists can securely view client-submitted intake details prior to the session via a seamless dashboard modal.
* **Virtual Therapy Rooms:** Integrated WebRTC/Jitsi video conferencing for secure, encrypted 1-on-1 sessions.
* **Time-Filtered Scheduling:** Dashboards automatically filter out past sessions to keep the UI clean and focused on upcoming appointments.

## 🛠️ Tech Stack

**Frontend**
* [Vue.js 3](https://vuejs.org/) (Composition API)
* [Vite](https://vitejs.dev/)
* Tailwind CSS (for rapid, responsive UI styling)
* Vue Router (for SPA navigation)

**Backend**
* [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python web framework)
* [SQLModel](https://sqlmodel.tiangolo.com/) (Combining SQLAlchemy and Pydantic)
* PyJWT (for secure token generation and validation)
* Uvicorn (ASGI web server)

**Database**
* MySQL

**Integrations & Testing Tools**
* Jitsi Meet API (Video Rooms)
* Cloudflare Tunnels / `untun` (For secure local network bypassing during mobile testing)

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites
* Node.js (v16+)
* Python (3.9+)
* MySQL Server

### 1. Database Setup
Ensure your MySQL server is running. Create a new database for the project:
```sql
CREATE DATABASE umoja_db;
```

### 2. Backend Setup (FastAPI)
Clone the repo and navigate to your backend directory and set up a virtual environment:

```bash
git clone https://github.com/chameja/umoja-therapy.git
```

```bash
# Create and activate virtual environment
cd umoja-therapy/app

python -m venv .venv
source .venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Run the server
fastapi dev --port 8090 --host 0.0.0.0
```

### 3. Frontend Setup (Vue.js)
Open a new terminal, navigate to your frontend directory, and install dependencies:

```bash
cd umoja-therapy/umoja-frontend
# Install NPM packages
npm install

# Run the development server
npm run dev
```

### 4. Environment Variables
You will need `.env` files in both your frontend and backend directories.

**Backend (`.env`)**
```ini
DATABASE_URL="mysql+pymysql://username:password@localhost/umoja_db"
SECRET_KEY="your-super-secret-jwt-key"
ALGORITHM="HS256"
```

**Frontend (`.env`)**
```ini
VITE_API_URL="http://localhost:8090" 
# Note: If testing on mobile via tunnels, update this to your backend's Cloudflare URL.
```

---

## 📱 Mobile Device Testing (Cloudflare Tunnels)
Because mobile browsers strictly enforce HTTPS for camera/microphone access, standard local network testing often fails. We use `untun` to generate secure, temporary HTTPS links.

Open two new terminals and run:

1. **Tunnel the Backend:** `npx untun@latest tunnel http://localhost:8090`
2. **Tunnel the Frontend:** `npx untun@latest tunnel http://localhost:5173`

*Important:* Be sure to update your frontend's `VITE_API_URL` to the newly generated backend tunnel URL before testing!

To test, open the frontend url on your laptop and phone. You can create new accounts or run the following command in the backend folder to generate seed data

```python
python seed.py
```

## Credentials
### Therapist
email: therapist1@umoja.com
password: password123

### Client
email: client1@umoja.com
password: password123

On your laptop, use the therapist account and client account on the phone. You can also use a laptop for the client account but for therapist, laptop is recommended or any other large screen device.

1. Create a session request with any of the therapists using the client account. The date and time must be a future date. Past dates and times won't show on the dashboard. You could optionally update your intake form as a client.
2. Login as the therapist whose session request you created.
3. After logging in as a therapist, you can see session requests, reject or accept them, and view the client's intake form responses.
4. After accepting a ssession request, go into the meeting room and click join meeting. For the first time, you'll have to login with jitsi using yout google account. So click the log-in button.
5. After that, you can join the meeting room on the phone as a client. If it doesn't show, you may have to reload the tab

---

## 📖 API Documentation
FastAPI automatically generates interactive API documentation. While the backend server is running, you can explore and test the endpoints directly from your browser:

* **Swagger UI:** `http://localhost:8090/docs`

---

*Built with purpose. Bridging the gap in mental healthcare.*
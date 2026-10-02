# 🔐 SecureVault

A secure full-stack file storage application built with **FastAPI, React, PostgreSQL, and JWT authentication**.

SecureVault allows users to securely upload, manage, download, and delete their files while enforcing user-level access control and file validation.

[![CI](https://github.com/anassofiyan/securevault/actions/workflows/ci.yml/badge.svg)](https://github.com/anassofiyan/securevault/actions)

---

## ✨ Features

- 🔐 JWT-based authentication
- 👤 User-level file authorization
- 📤 Secure file uploads
- 📥 File downloads
- 🗑️ File deletion
- 🛡️ MIME type & file-signature validation
- 📦 10 MB upload limit
- 🔑 UUID-based file storage
- 🗄️ PostgreSQL database
- 🔄 Alembic migrations
- 🧪 18 automated backend tests
- ⚙️ GitHub Actions CI
- ⚛️ React frontend with protected routes

---

## 🏗️ Architecture

```text
React + Vite
     │
     ▼
FastAPI REST API
     │
     ├── JWT Authentication
     ├── Authorization
     ├── File Validation
     │
     ├──────────────► PostgreSQL
     │                  │
     │                  └── File Metadata
     │
     └──────────────► File Storage

🛠️ Tech Stack
Layer	Technology
Frontend	React, Vite, React Router
Backend	Python, FastAPI
Database	PostgreSQL
ORM	SQLAlchemy
Migrations	Alembic
Authentication	JWT
Testing	Pytest
CI/CD	GitHub Actions


🔒 Security
SecureVault implements:
- JWT authentication with token expiration
- User-specific file authorization
- MIME type validation
- File signature validation
- File size restrictions
- UUID-based storage filenames
- Failed-upload cleanup
- Protected download and delete endpoints
🧪 Testing
The backend includes security-focused automated tests covering:
- Authentication
- User isolation
- File authorization
- Upload validation
- Invalid file signatures
- File size limits
- Database failures
- File cleanup
Current status: 18 tests passing ✅
Run locally:
cd backend
pytest -q

🚀 Run Locally
Backend
cd backend
python -m venv venv

Windows:
.\venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Create backend/.env:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/securevault
JWT_SECRET_KEY=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256
FRONTEND_ORIGIN=http://localhost:5173

Start the API:
uvicorn app.main:app --reload

Backend:
http://localhost:8000
API Docs:
http://localhost:8000/docs
Frontend
cd frontend
npm install

Create frontend/.env:
VITE_API_URL=http://localhost:8000

Start:
npm run dev

Frontend:
http://localhost:5173
📂 Project Structure
securevault/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── storage/
│   ├── test/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docker-compose.yml
└── README.md

🔌 API
Method	Endpoint	Description
POST	/register	Register user
POST	/login	Login
GET	/me	Current user
POST	/files/upload	Upload file
GET	/files	List files
GET	/files/{id}	Download file
DELETE	/files/{id}	Delete file


⚙️ CI
GitHub Actions automatically runs:
Backend Tests
      +
Frontend Build
      ↓
   SecureVault CI

Every push and pull request to main is checked automatically.
🔮 Future Improvements
- Cloud object storage
- Encryption at rest
- HttpOnly authentication cookies
- Refresh-token rotation
- Malware scanning
- Rate limiting
- Production deployment
👨‍💻 Author
Anas Sofiyan
Built with Python, FastAPI, React, PostgreSQL, and a slightly unreasonable amount of debugging.

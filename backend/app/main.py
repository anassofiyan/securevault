import os

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File as FastAPIFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from app.auth import get_current_user

from app.database import Base, engine, get_db
from app.models.user import User
from app.models.file import File
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.schemas.auth import TokenResponse
from app.schemas.file import (
    FileMetadataResponse,
    FileUploadResponse
)

load_dotenv()
MAX_FILE_SIZE = 10 * 1024 * 1024
BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = BASE_DIR / "storage"

STORAGE_DIR.mkdir(exist_ok=True)

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain"
}
def is_valid_file_content(file_data: bytes, content_type: str) -> bool:
    if content_type == "image/png":
        return file_data.startswith(b"\x89PNG\r\n\x1a\n")

    if content_type == "image/jpeg":
        return file_data.startswith(b"\xff\xd8\xff")

    if content_type == "application/pdf":
        return file_data.startswith(b"%PDF-")

    if content_type == "text/plain":
        try:
            file_data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    return False
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"

STORAGE_DIR.mkdir(exist_ok=True)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)   

# Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SecureVault API",
    description="Secure file storage backend",
    version="1.0.0"
)
FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "SecureVault API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(
        user_data.password
    )

    user = User(
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }

@app.post("/login",response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = pwd_context.verify(
        user_data.password,
        user.password_hash
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token_data = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me",  response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }

@app.post("/files/upload",response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Check file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=415,
            detail="File type not allowed"
        )

    # 2. Read the uploaded file
    CHUNK_SIZE = 1024 * 1024  # 1 MB

    file_data = bytearray()
    file_size = 0

    while True:
        chunk = await file.read(CHUNK_SIZE)

        if not chunk:
            break

        file_size += len(chunk)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 10 MB."
        )

        file_data.extend(chunk)

    file_data = bytes(file_data)

    if not is_valid_file_content(
        file_data,
        file.content_type
    ):
        raise HTTPException(
            status_code=415,
            detail="File content does not match the declared file type"
        )
    # 4. Generate a unique filename
    file_extension = ""

    if file.filename and "." in file.filename:
        file_extension = os.path.splitext(file.filename)[1]

    stored_filename = f"{uuid4()}{file_extension}"

    STORAGE_DIR.mkdir(exist_ok=True)

    file_path = STORAGE_DIR / stored_filename

    # 7. Save the actual file
    with open(file_path, "wb") as buffer:
        buffer.write(file_data)

    # 8. Save file metadata in PostgreSQL
    db_file = File(
        filename=file.filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        content_type=file.content_type,
        size=file_size,
        owner_id=current_user.id
    )

    try:
       db.add(db_file)
       db.commit()
       db.refresh(db_file)

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to save file"
        )

    return {
        "message": "File uploaded successfully",
        "file_id": db_file.id,
        "filename": db_file.filename,
        "size": db_file.size,
        "content_type": db_file.content_type
    }

@app.get("/files",response_model=list[FileMetadataResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = (
        db.query(File)
        .filter(File.owner_id == current_user.id)
        .all()
    )

    return [
        {
            "id": file.id,
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "created_at": file.created_at
        }
        for file in files
    ]   

@app.get("/files/{file_id}")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.owner_id == current_user.id
        )
        .first()
    )

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=404,
            detail="Stored file not found"
        )

    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type=file.content_type
    )

@app.delete("/files/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id,
            File.owner_id == current_user.id
        )
        .first()
    )

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if os.path.exists(file.file_path):
        os.remove(file.file_path)

    db.delete(file)
    db.commit()

    return {
        "message": "File deleted successfully",
        "file_id": file_id
    }
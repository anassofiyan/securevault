import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt
from datetime import datetime, timedelta, timezone

from app import main as main_module
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.file import File
from app.auth import SECRET_KEY, ALGORITHM


# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_test_environment(tmp_path, monkeypatch):
    # Reset the database before every test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Give every test its own temporary storage directory
    test_storage = tmp_path / "storage"
    test_storage.mkdir()

    monkeypatch.setattr(
        main_module,
        "STORAGE_DIR",
        test_storage
    )

    yield

    # Clean database after the test
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


def create_token(user_id, email):
    token_data = {
        "user_id": user_id,
        "email": email
    }

    return jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def test_files_requires_authentication():
    response = client.get("/files")

    assert response.status_code == 401


def test_user_cannot_access_another_users_file():
    db = TestingSessionLocal()

    # Create User 1
    user1 = User(
        email="testuser1@example.com",
        password_hash="fake-hash"
    )

    # Create User 2
    user2 = User(
        email="testuser2@example.com",
        password_hash="fake-hash"
    )

    db.add_all([user1, user2])
    db.commit()

    db.refresh(user1)
    db.refresh(user2)

    # Create a file owned by User 1
    test_file = File(
        filename="private.txt",
        stored_filename="test-private.txt",
        file_path="storage/test-private.txt",
        content_type="text/plain",
        size=100,
        owner_id=user1.id
    )

    db.add(test_file)
    db.commit()
    db.refresh(test_file)

    # Authenticate as User 2
    user2_token = create_token(
        user2.id,
        user2.email
    )

    response = client.get(
        f"/files/{test_file.id}",
        headers={
            "Authorization": f"Bearer {user2_token}"
        }
    )

    assert response.status_code == 404

    db.close()

def test_user_can_access_own_file(tmp_path):
    db = TestingSessionLocal()

    # Create User 1
    user1 = User(
        email="owner@example.com",
        password_hash="fake-hash"
    )

    db.add(user1)
    db.commit()
    db.refresh(user1)

    # Create an actual temporary file
    actual_file = tmp_path / "my-file.txt"
    actual_file.write_text("This is a test file.")

    # Create database record for the file
    test_file = File(
        filename="my-file.txt",
        stored_filename="my-file.txt",
        file_path=str(actual_file),
        content_type="text/plain",
        size=50,
        owner_id=user1.id
    )

    db.add(test_file)
    db.commit()
    db.refresh(test_file)

    # Authenticate as User 1
    user1_token = create_token(
        user1.id,
        user1.email
    )

    response = client.get(
        f"/files/{test_file.id}",
        headers={
            "Authorization": f"Bearer {user1_token}"
        }
    )

    assert response.status_code == 200

    db.close()

def test_user_can_delete_own_file(tmp_path):
    db = TestingSessionLocal()

    user1 = User(
        email="delete-owner@example.com",
        password_hash="fake-hash"
    )

    db.add(user1)
    db.commit()
    db.refresh(user1)

    actual_file = tmp_path / "delete-me.txt"
    actual_file.write_text("Delete this test file.")

    test_file = File(
        filename="delete-me.txt",
        stored_filename="delete-me.txt",
        file_path=str(actual_file),
        content_type="text/plain",
        size=22,
        owner_id=user1.id
    )

    db.add(test_file)
    db.commit()
    db.refresh(test_file)

    user1_token = create_token(
        user1.id,
        user1.email
    )

    response = client.delete(
        f"/files/{test_file.id}",
        headers={
            "Authorization": f"Bearer {user1_token}"
        }
    )

    assert response.status_code == 200
    assert not actual_file.exists()

    db.close()

def test_user_cannot_delete_another_users_file(tmp_path):
    db = TestingSessionLocal()

    user1 = User(
        email="delete-owner2@example.com",
        password_hash="fake-hash"
    )

    user2 = User(
        email="delete-other@example.com",
        password_hash="fake-hash"
    )

    db.add_all([user1, user2])
    db.commit()

    db.refresh(user1)
    db.refresh(user2)

    actual_file = tmp_path / "protected.txt"
    actual_file.write_text("Protected file.")

    test_file = File(
        filename="protected.txt",
        stored_filename="protected.txt",
        file_path=str(actual_file),
        content_type="text/plain",
        size=15,
        owner_id=user1.id
    )

    db.add(test_file)
    db.commit()
    db.refresh(test_file)

    user2_token = create_token(
        user2.id,
        user2.email
    )

    response = client.delete(
        f"/files/{test_file.id}",
        headers={
            "Authorization": f"Bearer {user2_token}"
        }
    )

    assert response.status_code == 404
    assert actual_file.exists()

    db.close()

def test_valid_file_upload():
    db = TestingSessionLocal()

    user = User(
        email="upload-user@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "test.txt",
                b"Hello SecureVault!",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200
    
    db.close()

def test_invalid_file_type():
    db = TestingSessionLocal()

    user = User(
        email="invalid-type@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "malware.exe",
                b"fake executable content",
                "application/x-msdownload"
            )
        }
    )

    assert response.status_code == 415

    db.close()
def test_file_too_large():
    db = TestingSessionLocal()

    user = User(
        email="large-file@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    large_file = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "large.txt",
                large_file,
                "text/plain"
            )
        }
    )

    assert response.status_code == 413

    db.close()

def test_invalid_jwt():
    response = client.get(
        "/files",
        headers={
            "Authorization": "Bearer this-is-not-a-real-token"
        }
    )

    assert response.status_code == 401
def test_token_for_nonexistent_user():
    token = create_token(
        999999,
        "ghost@example.com"
    )

    response = client.get(
        "/files",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
def test_expired_jwt():
    expired_token_data = {
        "user_id": 1,
        "email": "expired@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }

    expired_token = jwt.encode(
        expired_token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/files",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401
def test_download_when_physical_file_is_missing():
    db = TestingSessionLocal()

    user = User(
        email="missing-file@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    missing_file = File(
        filename="missing.txt",
        stored_filename="missing.txt",
        file_path="this-file-does-not-exist.txt",
        content_type="text/plain",
        size=100,
        owner_id=user.id
    )

    db.add(missing_file)
    db.commit()
    db.refresh(missing_file)

    token = create_token(
        user.id,
        user.email
    )

    response = client.get(
        f"/files/{missing_file.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stored file not found"

    db.close()

def test_delete_when_physical_file_is_missing():
    db = TestingSessionLocal()

    user = User(
        email="delete-missing@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    missing_file = File(
        filename="already-gone.txt",
        stored_filename="already-gone.txt",
        file_path="this-file-does-not-exist.txt",
        content_type="text/plain",
        size=100,
        owner_id=user.id
    )

    db.add(missing_file)
    db.commit()
    db.refresh(missing_file)

    file_id = missing_file.id

    token = create_token(
        user.id,
        user.email
    )

    response = client.delete(
        f"/files/{file_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    deleted_file = (
        db.query(File)
        .filter(File.id == file_id)
        .first()
    )

    assert deleted_file is None

    db.close()

def test_upload_cleans_up_file_when_database_commit_fails(monkeypatch):
    db = TestingSessionLocal()

    user = User(
        email="db-failure@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    def fake_commit():
        raise Exception("Simulated database failure")

    monkeypatch.setattr(db, "commit", fake_commit)

    def override_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_test_db

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "failure.txt",
                b"This upload should be cleaned up.",
                "text/plain"
            )
        }
    )

    assert response.status_code == 500

    # The database should not contain the failed upload
    failed_file = (
        db.query(File)
        .filter(File.filename == "failure.txt")
        .first()
    )

    assert failed_file is None

    # The temporary storage directory should contain no uploaded file
    stored_files = list(main_module.STORAGE_DIR.iterdir())

    assert stored_files == []

    app.dependency_overrides[get_db] = override_get_db

    db.close()

def test_rejects_fake_png_file():
    db = TestingSessionLocal()

    user = User(
        email="fake-png@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    fake_png_content = b"This is not actually a PNG file."

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "fake.png",
                fake_png_content,
                "image/png"
            )
        }
    )

    assert response.status_code == 415

    db.close()

def test_rejects_fake_jpeg_file():
    db = TestingSessionLocal()

    user = User(
        email="fake-jpeg@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "fake.jpg",
                b"This is not actually a JPEG file.",
                "image/jpeg"
            )
        }
    )

    assert response.status_code == 415

    db.close()

def test_rejects_fake_pdf_file():
    db = TestingSessionLocal()

    user = User(
        email="fake-pdf@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "fake.pdf",
                b"This is not actually a PDF file.",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 415

    db.close()

def test_oversized_upload_does_not_leave_file():
    db = TestingSessionLocal()

    user = User(
        email="oversized-cleanup@example.com",
        password_hash="fake-hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(
        user.id,
        user.email
    )

    large_file = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/files/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "huge.txt",
                large_file,
                "text/plain"
            )
        }
    )

    assert response.status_code == 413

    stored_files = list(main_module.STORAGE_DIR.iterdir())

    assert stored_files == []

    db.close()
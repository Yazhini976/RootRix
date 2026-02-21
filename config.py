import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Use environment variable for DB, fallback to local PostgreSQL for development
# Render provides DATABASE_URL automatically if you add a PostgreSQL instance
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:972006@localhost/ctf_platform")

# Support Render's 'postgres://' vs SQLAlchemy's 'postgresql://' requirement
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get("SECRET_KEY", "ctf_super_secret_key_rootrix_2025")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip", "txt", "pcap", "docx", "mp3", "mp4"}

SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False

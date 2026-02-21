import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:972006@localhost/ctf_platform"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "ctf_super_secret_key_rootrix_2025"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip", "txt", "pcap", "docx", "mp3", "mp4"}

SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False

"""Configuration partagée (MongoDB via fichier .env)."""
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


def load_env_file() -> None:
    """Charge les variables depuis .env à la racine du projet."""
    env_path = ROOT_DIR / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

MONGODB_URI = os.environ.get("MONGODB_URI", "").strip()
DATABASE_NAME = os.environ.get("DATABASE_NAME", "student_depression_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "students")

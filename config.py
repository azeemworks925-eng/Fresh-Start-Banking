"""Application settings, read from environment variables (.env file).

No credentials live in the code. Copy .env.example to .env and fill it in.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# The original university database must never be touched by this app.
PROTECTED_DB_NAME = "db_final_group_project"


@dataclass(frozen=True)
class DBSettings:
    host: str
    port: int
    user: str
    password: str
    database: str


def get_db_settings() -> DBSettings:
    settings = DBSettings(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "DB_Final_Group_Project_Working"),
    )
    if settings.database.lower() == PROTECTED_DB_NAME:
        raise RuntimeError(
            "DB_NAME points at the original database. This app only connects to the "
            "'_Working' copy. Change DB_NAME in your .env file."
        )
    return settings


# Hide most of every e-mail address and phone number in the UI (good for public screenshots).
MASK_PII = os.getenv("MASK_PII", "true").strip().lower() in {"1", "true", "yes"}

APP_TITLE ="Fresh-Start Bank"
APP_SUBTITLE = "Retail & Islamic Banking Administration"

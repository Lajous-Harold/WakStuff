import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://wakstuff:wakstuff@db:5432/wakstuff",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WAKFU_API_BASE_URL = os.getenv("WAKFU_API_BASE_URL", "").rstrip("/")
    ICON_BASE_URL = os.getenv("ICON_BASE_URL", "").rstrip("/")

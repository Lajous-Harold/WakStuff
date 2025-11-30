import os


class Config:
    # DB
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://wakstuff:wakstuff@db:5432/wakstuff",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Wakfu (optionnelle en V1, stub si vide)
    WAKFU_API_BASE_URL = os.getenv("WAKFU_API_BASE_URL", "").rstrip("/")

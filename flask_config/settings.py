import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///wuts.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_NAME = os.getenv("APP_NAME", "Wellness Updating & Tracking System")
    APP_SHORT_NAME = os.getenv("APP_SHORT_NAME", "WUTS")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "Your Company")
    APP_BRAND = os.getenv("APP_BRAND", f"{COMPANY_NAME} - {APP_SHORT_NAME}")

    WUTS_USERNAME = os.getenv("WUTS_USERNAME")
    WUTS_PASSWORD_HASH = os.getenv("WUTS_PASSWORD_HASH")

    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
    NOTIFY_CC = os.getenv("NOTIFY_CC")
    POWER_BI_EMBEDS = [
        {"url": os.getenv(f"POWER_BI_EMBED_URL_{i}"), "title": os.getenv(f"POWER_BI_EMBED_TITLE_{i}", f"Power BI Dashboard {i}")}
        for i in range(1, 10)
        if os.getenv(f"POWER_BI_EMBED_URL_{i}")
    ]

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

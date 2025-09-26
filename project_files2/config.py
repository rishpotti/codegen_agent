import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
    # Add other configuration variables here

from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

BASE_DIR = Path(__file__).parent.parent

class Setting(BaseSettings):
    db_url: str = os.getenv("DATABASE_URL")
    db_echo: bool = True

settings = Setting()
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Config(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    admin:str = os.getenv("ADMIN_NAME")
    password:str = os.getenv("ADMIN_PASSWORD")

def get_config() -> Config:
    return Config()
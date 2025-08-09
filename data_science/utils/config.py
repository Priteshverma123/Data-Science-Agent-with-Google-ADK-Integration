import os
from dotenv import load_dotenv


class Config:
    DEBUG = False
    TESTING = False
    FILE_TYPE = os.getenv("FILE_TYPE", "pdf,image")  # pdf,image,docx



class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
class ProductionConfig(Config):
    ENV = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = "testing"
    



config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def load_env_variables():
    """Load environment variables from .env file."""

    load_dotenv(dotenv_path=".env")
    env_name = os.getenv("FLASK_ENV", "development")
    return env_name


def load_env_variables_test():
    """Load environment variables from .env file."""
    load_dotenv()
    env_name = os.getenv("FLASK_ENV", "testing")
    return env_name


env_name = load_env_variables()
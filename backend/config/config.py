from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional, List
import os

class Settings(BaseSettings):
    env: str = "development"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    ALLOWED_DOMAINS: Optional[List[str]] = []

    model_config = {
        "env_file": ".env",
        "enable_decoding": "utf-8"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Jeśli nie ma zmiennych środowiskowych, użyj wartości domyślnych
        if not self.SUPABASE_URL:
            self.SUPABASE_URL = os.getenv("SUPABASE_URL", "https://demo.supabase.co")
        if not self.SUPABASE_KEY:
            self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", "demo-key")

settings = Settings()
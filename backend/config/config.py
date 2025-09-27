from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional, List

class Settings(BaseSettings):
    env: str = "development"
    SUPABASE_URL: AnyHttpUrl
    SUPABASE_KEY: str

    ALLOWED_DOMAINS: Optional[List[str]] = []

    model_config = {
        "env_file": ".env",
        "enable_decoding": "utf-8"
    }



settings = Settings()
print(settings)
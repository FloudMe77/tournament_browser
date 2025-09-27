import os
from config.config import settings
from supabase import create_client, Client
from typing import Generator

supabase: Client = create_client(str(settings.SUPABASE_URL), settings.SUPABASE_KEY)

def get_db() -> Client:
    return supabase


import os
from config.config import settings
from supabase import create_client, Client

def get_db() -> Client:
    supabase: Client = create_client(str(settings.SUPABASE_URL), settings.SUPABASE_KEY)
    return supabase

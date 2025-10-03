from typing import List, Optional, Dict, Any
from supabase import Client

TABLE_NAME = "users"


class UserRepository:
    def __init__(self, db: Client) -> None:
        self._db = db

    def get_username_by_id(self, user_id: str) -> Optional[str]:
        response = self._db.table(TABLE_NAME).select("username").eq("user_id", user_id).execute()
        if not response.data:
            return None
        return response.data[0].get("username")

    def get_user_id_by_username(self, username: str) -> Optional[str]:
        response = self._db.table(TABLE_NAME).select("user_id").eq("username", username).execute()
        if not response.data:
            return None
        return response.data[0].get("user_id")

    def list_all(self) -> List[Dict[str, Any]]:
        response = self._db.table(TABLE_NAME).select("*").execute()
        return response.data or []

    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self._db.table(TABLE_NAME).select("*").eq("user_id", user_id).limit(1).execute()
        if not response.data:
            return None
        return response.data[0]

    def update_by_user_id(self, user_id: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = (
            self._db.table(TABLE_NAME)
            .update(data)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data or []

    def search_usernames_prefix_excluding_user(self, prefix: str, exclude_user_id: str) -> List[str]:
        response = (
            self._db.table(TABLE_NAME)
            .select("username")
            .ilike("username", f"{prefix}%")
            .neq("user_id", exclude_user_id)
            .execute()
        )
        return [row["username"] for row in (response.data or [])] 
    
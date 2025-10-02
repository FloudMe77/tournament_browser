from typing import List, Dict, Any, Optional
from supabase import Client

FRIEND_LIST_VIEW = "user_friend_list"
INVITATION_VIEW = "invitation_pending_for_user"
FRIEND_TABLE = "friendship_request"


class FriendRepository:
    def __init__(self, db: Client) -> None:
        self._db = db

    def list_friends_usernames(self, user_id: str) -> List[str]:
        response = (
            self._db.table(FRIEND_LIST_VIEW)
            .select("friend_username")
            .eq("user_id", user_id)
            .execute()
        )
        return [row["friend_username"] for row in (response.data or [])]

    def list_invitations_created_by_user(self, user_id: str) -> List[str]:
        response = (
            self._db.table(INVITATION_VIEW)
            .select("friend_username")
            .eq("user_id", user_id)
            .execute()
        )
        return [row["friend_username"] for row in (response.data or [])]

    def list_invitations_for_user(self, friend_id: str) -> List[str]:
        response = (
            self._db.table(INVITATION_VIEW)
            .select("inviter_username")
            .eq("friend_id", friend_id)
            .execute()
        )
        return [row["inviter_username"] for row in (response.data or [])]

    def are_already_friends(self, user_id: str, other_username: str) -> bool:
        response = (
            self._db.table(FRIEND_LIST_VIEW)
            .select("friend_username")
            .eq("user_id", user_id)
            .eq("friend_username", other_username)
            .execute()
        )
        return bool(response.data)

    def invitation_exists_from_other_to_user(self, friend_id: str, other_user_id: str) -> bool:
        response = (
            self._db.table(INVITATION_VIEW)
            .select("inviter_username")
            .eq("friend_id", friend_id)
            .eq("user_id", other_user_id)
            .execute()
        )
        return bool(response.data)

    def invitation_exists_from_user_to_other(self, user_id: str, other_friend_id: str) -> bool:
        response = (
            self._db.table(INVITATION_VIEW)
            .select("inviter_username")
            .eq("friend_id", other_friend_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    def create_invitation(self, inviter_id: str, invitee_id: str) -> List[Dict[str, Any]]:
        data = {"inviter": inviter_id, "invitee": invitee_id}
        response = self._db.table(FRIEND_TABLE).insert(data).execute()
        return response.data or []

    def update_invitation_status(self, inviter_id: str, invitee_id: str, from_status: str, to_status: str) -> List[Dict[str, Any]]:
        response = (
            self._db.table(FRIEND_TABLE)
            .update({"status": to_status})
            .eq("invitee", invitee_id)
            .eq("inviter", inviter_id)
            .eq("status", from_status)
            .execute()
        )
        return response.data or []

    def invitation_exists(self, inviter_id: str, invitee_id: str) -> bool:
        response = (
            self._db.table(INVITATION_VIEW)
            .select("*")
            .eq("friend_id", invitee_id)
            .eq("user_id", inviter_id)
            .execute()
        )
        return bool(response.data) 
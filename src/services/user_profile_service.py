from models.enum import ToDoStatusEnum
from models.user_profile import UserProfile
from repositories.user_profile_repository import UserProfileRepository
from utils.helper import utc_now_iso


class UserProfileService:
    def __init__(self, user_profile_repo: UserProfileRepository = None):
        self.user_profile_repo = user_profile_repo or UserProfileRepository()

    def create(self, user_id: str, data: dict) -> UserProfile:
        timestamp = utc_now_iso()

        user_profile = UserProfile(
            id=user_id, date_created=timestamp, date_modified=timestamp, **data
        )
        self.user_profile_repo.create(user_profile)

        return user_profile

    def get(self, user_id: str) -> UserProfile:
        item = self.user_profile_repo.get(user_id)
        if not item:
            raise ValueError("Not Found")
        return UserProfile.from_dynamo(item)

    def update(self, user_id: str, data: dict) -> UserProfile:
        existing = self.user_profile_repo.get(user_id=user_id)
        if not existing:
            raise ValueError("Not Found")

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Title must be a non-empty string")
        else:
            title = existing["title"]

        description = data.get("description", existing.get("description"))

        if "status" in data:
            status_raw = data["status"]
            try:
                status = ToDoStatusEnum(status_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid status: '{status_raw}'. "
                    f"Expected one of: {[s.value for s in ToDoStatusEnum]}"
                )
        else:
            status = existing["status"]

        updated_user_profile = UserProfile(
            id=existing["id"],
            title=title,
            description=description,
            status=status,
            date_created=existing["date_created"],
            date_modified=utc_now_iso(),
        )
        self.user_profile_repo.update(user_profile=updated_user_profile)

        return updated_user_profile

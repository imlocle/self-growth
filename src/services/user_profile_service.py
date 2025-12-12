from models.user_profile import UserProfile
from repositories.user_profile_repository import UserProfileRepository
from utils.helper import utc_now_iso, validate_dict_str_value


class UserProfileService:
    def __init__(self, user_profile_repo: UserProfileRepository = None):
        self.user_profile_repo = user_profile_repo or UserProfileRepository()

    def create(self, user_id: str, data: dict) -> UserProfile:
        existing = self.user_profile_repo.get(user_id=user_id)
        if existing:
            raise ValueError("User already has a profile")

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
        user_profile = self.get(user_id=user_id)

        user_profile.username = validate_dict_str_value(
            data, "username", user_profile.username
        )
        user_profile.first_name = validate_dict_str_value(
            data, "first_name", user_profile.first_name
        )
        user_profile.last_name = validate_dict_str_value(
            data, "last_name", user_profile.last_name
        )

        self.user_profile_repo.update(user_profile=user_profile)

        return user_profile

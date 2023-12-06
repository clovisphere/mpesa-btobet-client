from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.repository.base import BaseRepository
from app.schema.profile import ProfileCreate, ProfileUpdate


class ProfileRepository(BaseRepository[Profile, ProfileCreate, ProfileUpdate]):
    def get_profile_by_msisdn(self, db: Session, phone_number: str) -> Profile | None:
        return db.query(Profile)\
                .filter(Profile.msisdn == phone_number)\
                .first()

    def get_profile_by_hashed_msisdn(self, db: Session, hashed_msisdn: str) -> Profile | None:
        return db.query(Profile)\
                .filter(Profile.hashed_msisdn == hashed_msisdn)\
                .first()


# profile 😁
profile = ProfileRepository(Profile)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import repository
from app.deps import get_db_session
from app.schema.profile import ProfileInDB


router = APIRouter()


@router.get("/msisdn/{msisdn}", response_model=ProfileInDB)
def get_profile_by_msisdn(msisdn: str, db: Session = Depends(get_db_session)):
    """Get (user) profile using the MSISDN."""
    profile = repository.profile.get_profile_by_msisdn(db, phone_number=msisdn)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile

@router.get("/hashed-msisdn/{hashed_msisdn}", response_model=ProfileInDB)
def get_profile_by_hashed_msisdn(hashed_msisdn: str, db: Session = Depends(get_db_session)):
    """Get (user) profile using the hashed MSISDN."""
    profile = repository.profile.get_profile_by_hashed_msisdn(db, hashed_msisdn=hashed_msisdn)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile

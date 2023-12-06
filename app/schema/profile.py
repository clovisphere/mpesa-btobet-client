from pydantic import BaseModel


class ProfileBase(BaseModel):
    msisdn: str
    hashed_msisdn: str


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileInDB(ProfileBase):
    id: int

    class Config:
        from_attributes = True

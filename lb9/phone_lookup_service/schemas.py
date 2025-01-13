from pydantic import BaseModel

class LookupRequest(BaseModel):
    phone_number: str

class LookupResponse(BaseModel):
    phone_number: str
    result: str

class PhoneOwnerCreate(BaseModel):
    phone_number: str
    owner_name: str
    additional_info: str = None

class PhoneOwnerResponse(BaseModel):
    phone_number: str
    owner_name: str
    additional_info: str = None

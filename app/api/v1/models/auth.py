from pydantic import BaseModel

class SignupRequest(BaseModel):
    email: str

class SignupResponse(BaseModel):
    user_id: str
    private_key: str
    public_key: str
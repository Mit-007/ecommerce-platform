from pydantic import BaseModel, EmailStr, Field

class RegisterCustomerRequest(BaseModel):
    name: str = Field(...,min_length=1,description="Customer name",)
    email: EmailStr = Field(...,description="Customer email address",)
    password: str = Field(...,min_length=8,description="Customer password",)

class LoginCustomerRequest(BaseModel):
    email: EmailStr = Field(...,description="Customer email address",)
    password: str = Field(...,min_length=1,description="Customer password",)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChnagePassword(BaseModel):
    new_password : str = Field(...,min_length=8,description="Customer new password",)
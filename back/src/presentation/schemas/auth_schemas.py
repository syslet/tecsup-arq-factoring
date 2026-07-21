from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyRegisterSchema(BaseModel):
    """Payload for registering company information."""

    ruc: str = Field(..., description="Peruvian RUC (11 numeric digits)")
    business_name: str = Field(..., min_length=3, description="Company business name")
    bank_name: str = Field(..., description="Bank name (e.g. BCP, BBVA, Interbank)")
    bank_account_number: str = Field(..., description="Bank account number")
    cci: str = Field(..., description="CCI account number (20 numeric digits)")
    currency: str = Field("PEN", description="Account currency (PEN or USD)")


class RegisterRequestSchema(BaseModel):
    """Payload for user and company registration."""

    email: EmailStr = Field(..., description="Legal representative email address")
    password: str = Field(..., description="Strong user password")
    full_name: str = Field(..., min_length=2, description="Legal representative full name")
    dni: str = Field(..., description="Peruvian DNI (8 numeric digits)")
    phone: str | None = Field(None, description="Contact phone number")
    company: CompanyRegisterSchema | None = Field(None, description="Company registration details")


class LoginRequestSchema(BaseModel):
    """Payload for user login using Email or DNI."""

    identifier: str = Field(..., description="User email address or DNI")
    password: str = Field(..., description="User password")


class CompanyResponseSchema(BaseModel):
    """Response structure for Company entity data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ruc: str
    business_name: str
    bank_name: str
    currency: str


class UserResponseSchema(BaseModel):
    """Response structure for User entity data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    dni: str
    phone: str | None = None
    role: str
    verification_status: str
    is_active: bool
    is_locked: bool
    company: CompanyResponseSchema | None = None
    created_at: datetime | None = None


class AuthTokenResponseSchema(BaseModel):
    """Response structure returned on successful login."""

    access_token: str
    token_type: str = "Bearer"
    user: UserResponseSchema
    expires_at: str


class MessageResponseSchema(BaseModel):
    """Generic message response."""

    message: str

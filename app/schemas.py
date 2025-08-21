from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr, field_validator
import bleach

# ---------------- User Schemas ----------------
class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True  # Pydantic v2
    }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------------- Transaction Schemas ----------------
CurrencyStr = constr(pattern=r"^[A-Z]{3}$")  # 3-letter currency code

class TransactionBase(BaseModel):
    amount: float = Field(gt=0)
    currency: CurrencyStr
    description: Optional[constr(max_length=280)] = None

    @field_validator("description")
    def sanitize_desc(cls, v):
        if v is None:
            return v
        return bleach.clean(v, tags=[], attributes={}, strip=True)

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[CurrencyStr] = None
    description: Optional[constr(max_length=280)] = None

    @field_validator("description")
    def sanitize_desc(cls, v):
        if v is None:
            return v
        return bleach.clean(v, tags=[], attributes={}, strip=True)

class TransactionOut(TransactionBase):
    id: int
    owner_id: int

    model_config = {
        "from_attributes": True  # Pydantic v2
    }

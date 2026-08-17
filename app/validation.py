from pydantic import BaseModel,Field,field_validator
from typing import Optional

class ClientForm(BaseModel):
    outlet_name: str
    location: str
    status: int

    @field_validator("outlet_name", "location", mode="before")
    @classmethod
    def not_blank(cls, v: Optional[str]) -> str:
        if v is None or not str(v).strip():
            raise ValueError("This field cannot be empty.")
        return str(v).strip()

class BeverageForm(BaseModel):
    product_brand: str
    quantity: int = Field(gt=0, description="Must be at least 1 item")
    price: int = Field(ge=0, description="Cannot be negative")

    @field_validator("product_brand", mode="before")
    @classmethod
    def not_blank(cls, v: Optional[str]) -> str:
        if v is None or not str(v).strip():
            raise ValueError("This field cannot be empty.")
        return str(v).strip()
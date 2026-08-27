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

class OrderForm(BaseModel):
    client_id: int
    status: int
    grand_total: float

    @field_validator("client_id", mode="before")
    @classmethod
    def not_blank_client(cls, v: Optional[str]) -> int:
        if v is None or not str(v).strip():
            raise ValueError("Client ID cannot be empty.")
        return int(v)

    @field_validator("status", mode="before")
    @classmethod
    def not_blank_status(cls, v: Optional[str]) -> int:
        if v is None or not str(v).strip():
            raise ValueError("Status cannot be empty.")
        return int(v)

    @field_validator("grand_total", mode="before")
    @classmethod
    def not_blank_total(cls, v: Optional[str]) -> float:
        if v is None or not str(v).strip():
            raise ValueError("Grand total cannot be empty.")
        return float(v)

class OrderItemForm(BaseModel):
    beverage_id: int = Field(gt=0, description="Beverage must be selected from the dropdown")
    mrp: float = Field(ge=0, description="Price cannot be negative")
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")
    cases: int = Field(gt=0, description="Cases should be greater than zero")
    discount: float = Field(ge=0, description="Discount cannot be negative")
    total_price: float = Field(ge=0, description="Total price cannot be negative")

    @field_validator("beverage_id", mode="before")
    @classmethod
    def not_blank_beverage(cls, v: Optional[str]) -> int:
        if v is None or not str(v).strip():
            raise ValueError("Beverage ID cannot be empty.")
        return int(v)

    @field_validator("mrp", mode="before")
    @classmethod
    def not_blank_mrp(cls, v: Optional[str]) -> float:
        if v is None or not str(v).strip():
            raise ValueError("mrp cannot be blank")
        return float(v)

    @field_validator("quantity", mode="before")
    @classmethod
    def not_blank_quantity(cls, v: Optional[str]) -> int:
        if v is None or not str(v).strip():
            raise ValueError("Quantity cannot be blank")
        return int(v)

    @field_validator("cases", mode="before")
    @classmethod
    def not_blank_cases(cls, v: Optional[str]) -> int:
        if v is None or not str(v).strip():
            raise ValueError("Cases cannot be blank")
        return int(v)

    @field_validator("discount", mode="before")
    @classmethod
    def not_blank_discount(cls, v: Optional[str]) -> float:
        if v is None or not str(v).strip():
            raise ValueError("Discount cannot be blank")
        return float(v)

    @field_validator("total_price", mode="before")
    @classmethod
    def not_blank_total_price(cls, v: Optional[str]) -> float:
        if v is None or not str(v).strip():
            raise ValueError("Total price cannot be blank")
        return float(v)
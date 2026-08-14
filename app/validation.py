from pydantic import BaseModel, field_validator
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
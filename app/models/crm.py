"""CRM customer model."""

from datetime import datetime
from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: int = Field(..., description="Unique customer ID")
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")
    created_at: datetime = Field(..., description="Account creation timestamp")
    status: str = Field(..., description="'active' or 'inactive'")

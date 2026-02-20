"""Support ticket model."""

from datetime import datetime
from pydantic import BaseModel, Field


class SupportTicket(BaseModel):
    ticket_id: int = Field(..., description="Unique ticket ID")
    customer_id: int = Field(..., description="Customer who raised the ticket")
    subject: str = Field(..., description="Issue description")
    priority: str = Field(..., description="'high', 'medium', or 'low'")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
    status: str = Field(..., description="'open' or 'closed'")

"""Request models for assignment, technician status, and appointments."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AssignmentRequest(BaseModel):
    technician_id: int = Field(gt=0)


class TechnicianChangeRequest(AssignmentRequest):
    reason: str = Field(max_length=255)


class StatusRequest(BaseModel):
    to_status: str = Field(min_length=1, max_length=20)
    note: str | None = Field(default=None, max_length=255)


class AppointmentRequest(BaseModel):
    ticket_id: int = Field(gt=0)
    appointment_type: Literal["GIAO", "NHAN"]
    start_at: datetime
    end_at: datetime
    note: str | None = Field(default=None, max_length=255)

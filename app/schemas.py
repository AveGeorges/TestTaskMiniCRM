from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContactStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    max_load: Optional[int] = None


class OperatorResponse(OperatorBase):
    id: int
    created_at: datetime
    current_load: Optional[int] = None

    model_config = {"from_attributes": True}


class SourceBase(BaseModel):
    name: str


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceOperatorWeightBase(BaseModel):
    operator_id: int
    weight: int


class SourceOperatorWeightCreate(SourceOperatorWeightBase):
    pass


class SourceOperatorWeightResponse(SourceOperatorWeightBase):
    id: int
    source_id: int

    model_config = {"from_attributes": True}


class SourceDistributionConfig(BaseModel):
    operator_weights: List[SourceOperatorWeightCreate]


class LeadBase(BaseModel):
    external_id: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactBase(BaseModel):
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    status: str = "active"


class ContactCreate(BaseModel):
    external_id: str
    source_id: int
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    status: str
    created_at: datetime
    lead: LeadResponse
    source: SourceResponse
    operator: Optional[OperatorResponse] = None

    model_config = {"from_attributes": True}


class ContactStats(BaseModel):
    total_contacts: int
    contacts_by_source: dict
    contacts_by_operator: dict

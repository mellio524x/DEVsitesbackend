from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

# Contact Form Models
class ContactSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    company: Optional[str] = None
    project: Optional[str] = None
    message: str
    budget: Optional[str] = None
    status: str = Field(default="new")  # new, contacted, closed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContactSubmissionCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    project: Optional[str] = None
    message: str
    budget: Optional[str] = None

class ContactResponse(BaseModel):
    success: bool
    message: str
    id: str

# Project Inquiry Models
class ProjectInquiry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    project_type: str  # "basic" or "standard"
    include_domain: bool = False
    include_database: bool = False
    estimated_cost: float
    additional_details: Optional[str] = None
    status: str = Field(default="pending")  # pending, quoted, accepted, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectInquiryCreate(BaseModel):
    name: str
    email: EmailStr
    project_type: str
    include_domain: bool = False
    include_database: bool = False
    additional_details: Optional[str] = None

class ProjectInquiryResponse(BaseModel):
    success: bool
    estimated_cost: float
    message: str
    id: str

# Newsletter Models
class NewsletterSubscriber(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    subscribed: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NewsletterSignupCreate(BaseModel):
    email: EmailStr

class NewsletterResponse(BaseModel):
    success: bool
    message: str

# Company Stats Model
class CompanyStats(BaseModel):
    projects_completed: int
    client_satisfaction: int
    average_turnaround: int
    active_projects: int = 0
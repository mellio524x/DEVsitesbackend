from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Import our custom modules
from models import (
    ContactSubmissionCreate, ContactResponse,
    ProjectInquiryCreate, ProjectInquiryResponse,
    NewsletterSignupCreate, NewsletterResponse,
    CompanyStats
)
from database import database
from business_logic import calculate_project_cost, validate_project_type, generate_project_summary

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="DEVSITES404 API", version="1.0.0")

# Create API router
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_db():
    await database.connect()
    logger.info("DEVSITES404 API started successfully")

@app.on_event("shutdown")
async def shutdown_db():
    await database.disconnect()
    logger.info("DEVSITES404 API shutdown complete")

# API Routes

@api_router.get("/")
async def root():
    return {"message": "DEVSITES404 API is running", "version": "1.0.0"}

@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact_data: ContactSubmissionCreate):
    """Handle contact form submissions"""
    try:
        # Create contact submission
        contact = await database.create_contact(contact_data.dict())
        
        logger.info(f"New contact submission from {contact_data.email}")
        
        return ContactResponse(
            success=True,
            message="Thank you for your message! We'll get back to you within 24 hours.",
            id=contact.id
        )
    
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")

@api_router.post("/project-inquiry", response_model=ProjectInquiryResponse)
async def submit_project_inquiry(inquiry_data: ProjectInquiryCreate):
    """Handle project inquiries with cost estimation"""
    try:
        # Validate project type
        if not validate_project_type(inquiry_data.project_type):
            raise HTTPException(status_code=400, detail="Invalid project type")
        
        # Calculate estimated cost
        estimated_cost = calculate_project_cost(
            inquiry_data.project_type,
            inquiry_data.include_domain,
            inquiry_data.include_database
        )
        
        # Create inquiry record
        inquiry_dict = inquiry_data.dict()
        inquiry_dict["estimated_cost"] = estimated_cost
        
        inquiry = await database.create_project_inquiry(inquiry_dict)
        
        logger.info(f"New project inquiry from {inquiry_data.email} - ${estimated_cost}")
        
        return ProjectInquiryResponse(
            success=True,
            estimated_cost=estimated_cost,
            message="We'll prepare a detailed proposal and send it to you within 24 hours.",
            id=inquiry.id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing project inquiry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit project inquiry")

@api_router.post("/newsletter", response_model=NewsletterResponse)
async def subscribe_newsletter(newsletter_data: NewsletterSignupCreate):
    """Handle newsletter subscriptions"""
    try:
        await database.subscribe_newsletter(newsletter_data.email)
        
        logger.info(f"New newsletter subscription: {newsletter_data.email}")
        
        return NewsletterResponse(
            success=True,
            message="Successfully subscribed to our newsletter!"
        )
    
    except Exception as e:
        logger.error(f"Error processing newsletter signup: {str(e)}")
        # Don't raise error for newsletter signup failures
        return NewsletterResponse(
            success=True,
            message="Thank you for your interest! We'll keep you updated."
        )

@api_router.get("/stats", response_model=dict)
async def get_company_stats():
    """Get company statistics"""
    try:
        stats = await database.get_company_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting company stats: {str(e)}")
        # Return default stats if database fails
        return {
            "projects_completed": 100,
            "client_satisfaction": 99,
            "average_turnaround": 14,
            "total_contacts": 0,
            "total_inquiries": 0,
            "newsletter_subscribers": 0
        }

@api_router.get("/project-summary")
async def get_project_summary(
    project_type: str,
    include_domain: bool = False,
    include_database: bool = False
):
    """Get detailed project summary with pricing breakdown"""
    try:
        if not validate_project_type(project_type):
            raise HTTPException(status_code=400, detail="Invalid project type")
        
        summary = generate_project_summary(project_type, include_domain, include_database)
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating project summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate project summary")

# Admin routes (for future use)
@api_router.get("/admin/contacts")
async def get_contacts(skip: int = 0, limit: int = 100):
    """Get contact submissions (admin only)"""
    try:
        contacts = await database.get_contacts(skip, limit)
        return {"contacts": [contact.dict() for contact in contacts]}
    except Exception as e:
        logger.error(f"Error getting contacts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contacts")

@api_router.get("/admin/inquiries")
async def get_project_inquiries(skip: int = 0, limit: int = 100):
    """Get project inquiries (admin only)"""
    try:
        inquiries = await database.get_project_inquiries(skip, limit)
        return {"inquiries": [inquiry.dict() for inquiry in inquiries]}
    except Exception as e:
        logger.error(f"Error getting inquiries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve inquiries")

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from models import ContactSubmission, ProjectInquiry, NewsletterSubscriber
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_url = os.environ['MONGO_URL']
            db_name = os.environ['DB_NAME']
            
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Create unique index on newsletter email
            await self.db.newsletter_subscribers.create_index("email", unique=True)
            
            # Create indexes for better query performance
            await self.db.contacts.create_index("email")
            await self.db.contacts.create_index("created_at")
            await self.db.project_inquiries.create_index("email")
            await self.db.project_inquiries.create_index("created_at")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    # Contact methods
    async def create_contact(self, contact_data: dict) -> ContactSubmission:
        """Create a new contact submission"""
        contact = ContactSubmission(**contact_data)
        result = await self.db.contacts.insert_one(contact.dict())
        contact.id = str(result.inserted_id) if result.inserted_id else contact.id
        return contact
    
    async def get_contacts(self, skip: int = 0, limit: int = 100):
        """Get contact submissions with pagination"""
        cursor = self.db.contacts.find().skip(skip).limit(limit).sort("created_at", -1)
        contacts = await cursor.to_list(length=limit)
        return [ContactSubmission(**contact) for contact in contacts]
    
    async def update_contact_status(self, contact_id: str, status: str) -> bool:
        """Update contact submission status"""
        result = await self.db.contacts.update_one(
            {"id": contact_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # Project Inquiry methods
    async def create_project_inquiry(self, inquiry_data: dict) -> ProjectInquiry:
        """Create a new project inquiry"""
        inquiry = ProjectInquiry(**inquiry_data)
        result = await self.db.project_inquiries.insert_one(inquiry.dict())
        inquiry.id = str(result.inserted_id) if result.inserted_id else inquiry.id
        return inquiry
    
    async def get_project_inquiries(self, skip: int = 0, limit: int = 100):
        """Get project inquiries with pagination"""
        cursor = self.db.project_inquiries.find().skip(skip).limit(limit).sort("created_at", -1)
        inquiries = await cursor.to_list(length=limit)
        return [ProjectInquiry(**inquiry) for inquiry in inquiries]

    # Newsletter methods
    async def subscribe_newsletter(self, email: str) -> NewsletterSubscriber:
        """Subscribe email to newsletter"""
        try:
            subscriber = NewsletterSubscriber(email=email)
            result = await self.db.newsletter_subscribers.insert_one(subscriber.dict())
            subscriber.id = str(result.inserted_id) if result.inserted_id else subscriber.id
            return subscriber
        except Exception as e:
            if "duplicate key" in str(e).lower():
                # Email already exists, update subscription status
                await self.db.newsletter_subscribers.update_one(
                    {"email": email},
                    {"$set": {"subscribed": True, "updated_at": datetime.utcnow()}}
                )
                existing = await self.db.newsletter_subscribers.find_one({"email": email})
                return NewsletterSubscriber(**existing)
            raise
    
    async def get_newsletter_subscribers(self, active_only: bool = True):
        """Get newsletter subscribers"""
        filter_query = {"subscribed": True} if active_only else {}
        cursor = self.db.newsletter_subscribers.find(filter_query).sort("created_at", -1)
        subscribers = await cursor.to_list(length=None)
        return [NewsletterSubscriber(**sub) for sub in subscribers]
    
    # Stats methods
    async def get_company_stats(self) -> dict:
        """Get company statistics"""
        try:
            total_contacts = await self.db.contacts.count_documents({})
            total_inquiries = await self.db.project_inquiries.count_documents({})
            total_subscribers = await self.db.newsletter_subscribers.count_documents({"subscribed": True})
            
            # Calculate some basic stats
            projects_completed = total_inquiries + 85  # Add base number
            client_satisfaction = 100  # Static for now
            average_turnaround = 14  # 2 weeks
            
            return {
                "projects_completed": projects_completed,
                "client_satisfaction": client_satisfaction,
                "average_turnaround": average_turnaround,
                "total_contacts": total_contacts,
                "total_inquiries": total_inquiries,
                "newsletter_subscribers": total_subscribers
            }
        except Exception as e:
            logger.error(f"Error getting company stats: {str(e)}")
            # Return default stats if database query fails
            return {
                "projects_completed": 100,
                "client_satisfaction": 100,
                "average_turnaround": 14,
                "total_contacts": 0,
                "total_inquiries": 0,
                "newsletter_subscribers": 0
            }

# Global database instance
database = Database()
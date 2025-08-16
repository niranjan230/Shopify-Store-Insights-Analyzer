from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProductSchema(BaseModel):
    """Pydantic schema for product validation"""
    id: Optional[str] = None
    title: Optional[str] = None
    handle: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    available: Optional[bool] = None
    tags: Optional[List[str]] = []
    images: Optional[List[str]] = []
    url: Optional[str] = None

class FAQSchema(BaseModel):
    """Pydantic schema for FAQ validation"""
    question: str
    answer: str
    category: Optional[str] = None

class SocialHandleSchema(BaseModel):
    """Pydantic schema for social handle validation"""
    platform: str
    url: str
    handle: Optional[str] = None

class ContactInfoSchema(BaseModel):
    """Pydantic schema for contact information validation"""
    emails: List[str] = []
    phone_numbers: List[str] = []
    address: Optional[str] = None

class BrandInsightsSchema(BaseModel):
    """Pydantic schema for brand insights validation"""
    website_url: str
    brand_name: Optional[str] = None
    brand_description: Optional[str] = None
    product_catalog: List[ProductSchema] = []
    hero_products: List[ProductSchema] = []
    privacy_policy_url: Optional[str] = None
    privacy_policy_content: Optional[str] = None
    return_refund_policy_url: Optional[str] = None
    return_refund_policy_content: Optional[str] = None
    faqs: List[FAQSchema] = []
    social_handles: List[SocialHandleSchema] = []
    contact_info: Optional[ContactInfoSchema] = None
    important_links: Dict[str, str] = {}
    scraped_at: Optional[datetime] = None

    @validator('website_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class WebsiteUrlRequest(BaseModel):
    """Schema for API request validation"""
    website_url: str
    
    @validator('website_url')
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError('Website URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

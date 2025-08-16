from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

@dataclass
class Product:
    """Product data model"""
    id: Optional[str] = None
    title: Optional[str] = None
    handle: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    available: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    url: Optional[str] = None

@dataclass
class FAQ:
    """FAQ item model"""
    question: str
    answer: str
    category: Optional[str] = None

@dataclass
class SocialHandle:
    """Social media handle info"""
    platform: str
    url: str
    handle: Optional[str] = None

@dataclass
class ContactInfo:
    """Contact information model"""
    emails: List[str]
    phone_numbers: List[str]
    address: Optional[str] = None

@dataclass
class BrandInsights:
    """Main data model for all the brand info we collect"""
    website_url: str
    brand_name: Optional[str] = None
    brand_description: Optional[str] = None
    product_catalog: List[Product] = None
    hero_products: List[Product] = None
    privacy_policy_url: Optional[str] = None
    privacy_policy_content: Optional[str] = None
    return_refund_policy_url: Optional[str] = None
    return_refund_policy_content: Optional[str] = None
    faqs: List[FAQ] = None
    social_handles: List[SocialHandle] = None
    contact_info: Optional[ContactInfo] = None
    important_links: Dict[str, str] = None
    scraped_at: Optional[datetime] = None
    
    def __post_init__(self):
        # Set up default empty lists and dicts
        if self.product_catalog is None:
            self.product_catalog = []
        if self.hero_products is None:
            self.hero_products = []
        if self.faqs is None:
            self.faqs = []
        if self.social_handles is None:
            self.social_handles = []
        if self.important_links is None:
            self.important_links = {}
        if self.scraped_at is None:
            # Set timestamp to IST (UTC+5:30) - most shops are in India
            ist_timezone = timezone(timedelta(hours=5, minutes=30))
            self.scraped_at = datetime.now(ist_timezone)

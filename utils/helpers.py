import re
import logging
from typing import Optional, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean up text content - removes HTML and normalizes whitespace"""
    if not text:
        return ""
    
    # Get rid of extra whitespace and normalize
    text = ' '.join(text.split())
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\?\!\-\:\;\(\)\[\]\'\"\/\@\#\$\%\&\*\+\=]', '', text)
    
    return text.strip()

def extract_domain(url: str) -> Optional[str]:
    """Get the domain from a URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None

def normalize_url(url: str) -> str:
    """Make sure URLs are in the right format"""
    if not url:
        return url
    
    url = url.strip()
    
    # Add https:// if it's missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url

def extract_price_from_text(text: str) -> Optional[str]:
    """Extract price from text using regex patterns"""
    if not text:
        return None
    
    # Common price patterns
    price_patterns = [
        r'\$\s*(\d+(?:\.\d{2})?)',  # $19.99
        r'(\d+(?:\.\d{2})?)\s*USD',  # 19.99 USD
        r'Rs\.?\s*(\d+(?:\.\d{2})?)',  # Rs. 199.99
        r'₹\s*(\d+(?:\.\d{2})?)',  # ₹199.99
        r'€\s*(\d+(?:\.\d{2})?)',  # €19.99
        r'£\s*(\d+(?:\.\d{2})?)',  # £19.99
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None

def extract_emails_from_text(text: str) -> List[str]:
    """Extract email addresses from text"""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Filter out common non-email matches
    filtered_emails = []
    exclude_patterns = [
        r'@example\.',
        r'@domain\.',
        r'@test\.',
        r'noreply@',
        r'no-reply@'
    ]
    
    for email in emails:
        if not any(re.search(pattern, email.lower()) for pattern in exclude_patterns):
            filtered_emails.append(email.lower())
    
    return list(set(filtered_emails))

def extract_phone_numbers_from_text(text: str) -> List[str]:
    """Extract phone numbers from text"""
    if not text:
        return []
    
    # Phone number patterns
    phone_patterns = [
        r'\+\d{1,3}[\s\-]?\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # International format
        r'\(\d{3}\)[\s\-]?\d{3}[\s\-]?\d{4}',  # (123) 456-7890
        r'\d{3}[\s\-]\d{3}[\s\-]\d{4}',  # 123-456-7890
        r'\d{10,}',  # 1234567890
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    # Filter and clean phone numbers
    cleaned_numbers = []
    for number in phone_numbers:
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', number)
        if 10 <= len(digits_only) <= 15:
            cleaned_numbers.append(number.strip())
    
    return list(set(cleaned_numbers))

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + '...'

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_file_extension_from_url(url: str) -> Optional[str]:
    """Extract file extension from URL"""
    try:
        parsed = urlparse(url)
        path = parsed.path
        if '.' in path:
            return path.split('.')[-1].lower()
        return None
    except Exception:
        return None

def format_currency(amount: str) -> str:
    """Format currency string for consistency"""
    if not amount:
        return amount
    
    # Remove extra spaces
    amount = ' '.join(amount.split())
    
    # Standardize currency symbols
    replacements = {
        'USD': '$',
        'Rs.': '₹',
        'Rs': '₹',
    }
    
    for old, new in replacements.items():
        amount = amount.replace(old, new)
    
    return amount

def categorize_link(url: str, text: str) -> Optional[str]:
    """Categorize a link based on URL and text content"""
    url_lower = url.lower()
    text_lower = text.lower()
    
    categories = {
        'contact': ['contact', 'support', 'help'],
        'about': ['about', 'story', 'company'],
        'shipping': ['shipping', 'delivery'],
        'returns': ['return', 'refund', 'exchange'],
        'privacy': ['privacy', 'policy'],
        'terms': ['terms', 'conditions'],
        'faq': ['faq', 'frequently', 'questions'],
        'blog': ['blog', 'news', 'article'],
        'track': ['track', 'order', 'tracking'],
        'careers': ['career', 'job', 'hiring'],
        'wholesale': ['wholesale', 'bulk', 'b2b']
    }
    
    for category, keywords in categories.items():
        if any(keyword in url_lower or keyword in text_lower for keyword in keywords):
            return category
    
    return 'other'

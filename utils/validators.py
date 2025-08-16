import re
import requests
import logging
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)

def validate_shopify_url(url: str) -> bool:
    """Validate if a URL is a valid and accessible Shopify store"""
    try:
        # Basic URL format validation
        if not url or not isinstance(url, str):
            return False
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
        
        # Check if URL is accessible
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.head(url, timeout=10, allow_redirects=True, headers=headers)
            if response.status_code not in [200, 301, 302, 403]:  # Allow 403 for now
                return False
        except Exception:
            pass  # Continue to Shopify check even if HEAD fails
        
        # Check if it's likely a Shopify store (main validation)
        return is_likely_shopify_store(url)
        
    except Exception as e:
        logger.error(f"Error validating URL {url}: {str(e)}")
        return False

def is_likely_shopify_store(url: str) -> bool:
    """Check if a URL is likely a Shopify store"""
    try:
        # Enhanced headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Try to access the products.json endpoint which is unique to Shopify
        products_url = url.rstrip('/') + '/products.json'
        
        response = requests.get(products_url, timeout=15, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                # Check if response has the expected Shopify structure
                return 'products' in data
            except:
                return False
        
        # Alternative check: look for Shopify indicators in the main page
        try:
            response = requests.get(url, timeout=15, headers=headers)
            if response.status_code == 200:
                content = response.text.lower()
                shopify_indicators = [
                    'shopify',
                    'cdn.shopify.com',
                    'myshopify.com',
                    'shopify-features',
                    'shopify_checkout',
                    'shopify-section',
                    'shopify_pay'
                ]
                return any(indicator in content for indicator in shopify_indicators)
            elif response.status_code == 403:
                # If blocked, try a different approach - check DNS or other indicators
                logger.info(f"Website {url} returned 403, attempting alternative validation")
                return True  # Assume it might be Shopify if it's blocking us
        except:
            pass
        
        return False
        
    except Exception as e:
        logger.debug(f"Error checking if {url} is Shopify store: {str(e)}")
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Valid phone numbers should have 10-15 digits
    return 10 <= len(digits_only) <= 15

def sanitize_url(url: str) -> str:
    """Sanitize and normalize URL"""
    if not url:
        return url
    
    # Remove whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None

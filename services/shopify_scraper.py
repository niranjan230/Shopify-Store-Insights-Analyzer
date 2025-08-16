import requests
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from models import BrandInsights, Product
from utils.helpers import clean_text, extract_domain

logger = logging.getLogger(__name__)

class ShopifyScraper:
    """Scraper for getting shopify store data"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set up headers to look like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        self.timeout = 30
        self.max_retries = 3

    def scrape_store(self, website_url: str) -> BrandInsights:
        """Main scraping method - gets all the store data we need"""
        logger.info(f"Starting to scrape Shopify store: {website_url}")
        
        # Create new insights object for this store
        insights = BrandInsights(website_url=website_url)
        
        try:
            # First check if we can actually access the site
            if not self._verify_website_access(website_url):
                raise Exception("Website not accessible or not found")
            
            # Now get all the different types of data
            self._extract_brand_info(website_url, insights)
            
            # Get the full product list from products.json
            self._extract_product_catalog(website_url, insights)
            
            # Get products shown on homepage
            self._extract_hero_products(website_url, insights)
            
            # Get policy pages
            self._extract_policies(website_url, insights)
            
            # Get FAQ data
            self._extract_faqs(website_url, insights)
            
            # Get social media links
            self._extract_social_handles(website_url, insights)
            
            # Get contact info
            self._extract_contact_info(website_url, insights)
            
            # Get other important pages
            self._extract_important_links(website_url, insights)
            
            logger.info(f"Successfully scraped store: {website_url}")
            return insights
            
        except Exception as e:
            logger.error(f"Error scraping store {website_url}: {str(e)}")
            raise

    def _verify_website_access(self, url: str) -> bool:
        """Check if we can actually reach the website"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            # Some sites return 403 but still work, so we'll accept that
            return response.status_code in [200, 403]
        except Exception as e:
            logger.error(f"Cannot access website {url}: {str(e)}")
            return False

    def _make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic - handles rate limiting"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response
            elif response.status_code == 429 and retries < self.max_retries:
                # Rate limited - wait a bit and try again
                time.sleep(2 ** retries)
                return self._make_request(url, retries + 1)
            else:
                logger.warning(f"HTTP {response.status_code} for URL: {url}")
                return None
        except Exception as e:
            if retries < self.max_retries:
                time.sleep(1)
                return self._make_request(url, retries + 1)
            logger.error(f"Request failed for {url}: {str(e)}")
            return None

    def _extract_brand_info(self, website_url: str, insights: BrandInsights):
        """Extract basic brand information from the homepage"""
        response = self._make_request(website_url)
        if not response:
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple methods to extract brand name
        brand_name = None
        
        # Method 1: Look for site name in meta property
        site_name = soup.find('meta', attrs={'property': 'og:site_name'})
        if site_name and hasattr(site_name, 'get'):
            content = site_name.get('content', '')
            if isinstance(content, str) and content.strip():
                brand_name = clean_text(content)
        
        # Method 2: Look for application name
        if not brand_name:
            app_name = soup.find('meta', attrs={'name': 'application-name'})
            if app_name and hasattr(app_name, 'get'):
                content = app_name.get('content', '')
                if isinstance(content, str) and content.strip():
                    brand_name = clean_text(content)
        
        # Method 3: Extract from title tag (clean it up)
        if not brand_name:
            title_tag = soup.find('title')
            if title_tag:
                title_text = clean_text(title_tag.text)
                # Remove common suffixes to get clean brand name
                suffixes_to_remove = [' - Online Store', ' | Official Store', ' Store', ' Shop', ' Official Site', ' Website']
                for suffix in suffixes_to_remove:
                    if title_text.endswith(suffix):
                        title_text = title_text[:-len(suffix)].strip()
                        break
                # Take first part if there are separators
                if ' | ' in title_text:
                    brand_name = title_text.split(' | ')[0].strip()
                elif ' - ' in title_text:
                    brand_name = title_text.split(' - ')[0].strip()
                else:
                    brand_name = title_text
        
        # Method 4: Look for brand name in URL domain
        if not brand_name or len(brand_name.strip()) < 3:
            from urllib.parse import urlparse
            parsed = urlparse(website_url)
            domain = parsed.netloc.lower()
            # Remove www. and common TLDs
            domain = domain.replace('www.', '')
            if '.' in domain:
                domain_name = domain.split('.')[0]
                # Capitalize first letter
                brand_name = domain_name.capitalize()
        
        insights.brand_name = brand_name if brand_name and brand_name.strip() else 'Brand Name Not Available'
        
        # Extract brand description from meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and hasattr(meta_desc, 'get'):
            content = meta_desc.get('content', '')
            if isinstance(content, str):
                insights.brand_description = clean_text(content)

    def _extract_product_catalog(self, website_url: str, insights: BrandInsights):
        """Extract product catalog using Shopify's products.json endpoint"""
        products_url = urljoin(website_url, '/products.json')
        
        try:
            response = self._make_request(products_url)
            if response:
                products_data = response.json()
                products = products_data.get('products', [])
                
                for product_data in products:
                    product = self._parse_product_json(product_data, website_url)
                    insights.product_catalog.append(product)
                
                logger.info(f"Extracted {len(insights.product_catalog)} products from catalog")
        except Exception as e:
            logger.error(f"Error extracting product catalog: {str(e)}")

    def _extract_hero_products(self, website_url: str, insights: BrandInsights):
        """Extract hero products from the homepage"""
        response = self._make_request(website_url)
        if not response:
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for product links on homepage
        product_links = soup.find_all('a', href=True)
        hero_products = []
        
        for link in product_links:
            href = link.get('href', '') if hasattr(link, 'get') else ''
            if isinstance(href, str) and '/products/' in href:
                product_url = urljoin(website_url, href)
                if len(hero_products) < 10:  # Limit to first 10 hero products
                    product = self._scrape_individual_product(product_url)
                    if product:
                        hero_products.append(product)
        
        insights.hero_products = hero_products[:6]  # Keep top 6 hero products
        logger.info(f"Extracted {len(insights.hero_products)} hero products")

    def _parse_product_json(self, product_data: Dict, base_url: str) -> Product:
        """Parse product data from JSON response"""
        variants = product_data.get('variants', [])
        price = None
        compare_at_price = None
        available = False
        
        if variants:
            variant = variants[0]  # Use first variant
            price = variant.get('price')
            compare_at_price = variant.get('compare_at_price')
            available = variant.get('available', False)
        
        images = []
        for image in product_data.get('images', []):
            if isinstance(image, dict):
                images.append(image.get('src', ''))
            elif isinstance(image, str):
                images.append(image)
        
        return Product(
            id=str(product_data.get('id', '')),
            title=clean_text(product_data.get('title', '')),
            handle=product_data.get('handle', ''),
            description=clean_text(product_data.get('body_html', '')),
            vendor=product_data.get('vendor', ''),
            product_type=product_data.get('product_type', ''),
            price=price,
            compare_at_price=compare_at_price,
            available=available,
            tags=product_data.get('tags', []),
            images=images,
            url=urljoin(base_url, f"/products/{product_data.get('handle', '')}")
        )

    def _scrape_individual_product(self, product_url: str) -> Optional[Product]:
        """Scrape individual product page for detailed information"""
        response = self._make_request(product_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product information from the page
        title = soup.find('h1')
        title_text = clean_text(title.text) if title else ''
        
        # Look for price information
        def has_price_class(css_class):
            if css_class is None:
                return False
            if isinstance(css_class, list):
                return any('price' in str(c).lower() for c in css_class)
            return 'price' in str(css_class).lower()
        
        price_elem = soup.find(['span', 'div'], class_=has_price_class)
        price = clean_text(price_elem.text) if price_elem else None
        
        # Extract images
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags:
            src = img.get('src', '') if hasattr(img, 'get') else ''
            if isinstance(src, str) and ('product' in src.lower() or 'cdn.shopify' in src):
                images.append(src)
        
        return Product(
            title=title_text,
            price=price,
            images=images[:3],  # Limit to first 3 images
            url=product_url
        )

    def _extract_policies(self, website_url: str, insights: BrandInsights):
        """Extract privacy policy and return/refund policy"""
        # Common policy URLs in Shopify stores
        policy_urls = {
            'privacy': ['/pages/privacy-policy', '/privacy-policy', '/pages/privacy'],
            'return': ['/pages/return-policy', '/return-policy', '/pages/returns', '/pages/refund-policy']
        }
        
        # Extract privacy policy
        for path in policy_urls['privacy']:
            policy_url = urljoin(website_url, path)
            response = self._make_request(policy_url)
            if response:
                insights.privacy_policy_url = policy_url
                soup = BeautifulSoup(response.content, 'html.parser')
                content = soup.get_text()
                insights.privacy_policy_content = clean_text(content)[:2000]  # Limit content
                break
        
        # Extract return/refund policy
        for path in policy_urls['return']:
            policy_url = urljoin(website_url, path)
            response = self._make_request(policy_url)
            if response:
                insights.return_refund_policy_url = policy_url
                soup = BeautifulSoup(response.content, 'html.parser')
                content = soup.get_text()
                insights.return_refund_policy_content = clean_text(content)[:2000]  # Limit content
                break

    def _extract_faqs(self, website_url: str, insights: BrandInsights):
        """Extract FAQs from the website"""
        from services.content_extractor import ContentExtractor
        extractor = ContentExtractor()
        insights.faqs = extractor.extract_faqs(website_url)

    def _extract_social_handles(self, website_url: str, insights: BrandInsights):
        """Extract social media handles"""
        from services.content_extractor import ContentExtractor
        extractor = ContentExtractor()
        insights.social_handles = extractor.extract_social_handles(website_url)

    def _extract_contact_info(self, website_url: str, insights: BrandInsights):
        """Extract contact information"""
        from services.content_extractor import ContentExtractor
        extractor = ContentExtractor()
        insights.contact_info = extractor.extract_contact_info(website_url)

    def _extract_important_links(self, website_url: str, insights: BrandInsights):
        """Extract important links like order tracking, contact us, blogs"""
        response = self._make_request(website_url)
        if not response:
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        important_keywords = {
            'order_tracking': ['track', 'order', 'tracking'],
            'contact_us': ['contact', 'support'],
            'blog': ['blog', 'news', 'article'],
            'about': ['about'],
            'shipping': ['shipping'],
            'faq': ['faq', 'help']
        }
        
        for link in links:
            href_raw = link.get('href', '') if hasattr(link, 'get') else ''
            href = str(href_raw).lower() if href_raw else ''
            text = clean_text(link.text).lower()
            
            for category, keywords in important_keywords.items():
                if any(keyword in href or keyword in text for keyword in keywords):
                    full_url = urljoin(website_url, str(href_raw))
                    insights.important_links[category] = full_url
                    break

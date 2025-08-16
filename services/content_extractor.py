import re
import logging
from typing import List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from models import FAQ, SocialHandle, ContactInfo
from utils.helpers import clean_text

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extracts different types of content from web pages"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set up headers to look like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.timeout = 30

    def extract_faqs(self, website_url: str) -> List[FAQ]:
        """Get FAQs from the website - tries different common locations"""
        faqs = []
        
        # These are the most common FAQ page URLs I've seen
        faq_paths = ['/pages/faq', '/faq', '/pages/frequently-asked-questions', '/help', '/pages/help']
        
        logger.info(f"Looking for FAQs at {len(faq_paths)} common paths")
        
        for path in faq_paths:
            faq_url = urljoin(website_url, path)
            try:
                response = self.session.get(faq_url, timeout=self.timeout)
                if response.status_code == 200:
                    logger.info(f"Found FAQ page at: {faq_url}")
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_faqs = self._parse_faq_page(soup)
                    faqs.extend(page_faqs)
                    logger.info(f"Extracted {len(page_faqs)} FAQs from {faq_url}")
                    if faqs:  # If we found some FAQs, that's good enough
                        break
                else:
                    logger.debug(f"FAQ page {faq_url} returned status {response.status_code}")
            except Exception as e:
                logger.debug(f"Error checking FAQ URL {faq_url}: {str(e)}")
        
        # If no dedicated FAQ page, try to find FAQs on the main page
        if not faqs:
            logger.info("No dedicated FAQ page found, checking main page")
            try:
                response = self.session.get(website_url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    faqs = self._parse_faq_page(soup)
                    logger.info(f"Extracted {len(faqs)} FAQs from main page")
            except Exception as e:
                logger.error(f"Error extracting FAQs from main page: {str(e)}")
        
        logger.info(f"Total FAQs extracted: {len(faqs)}")
        return faqs[:10]  # Don't return too many FAQs

    def _parse_faq_page(self, soup: BeautifulSoup) -> List[FAQ]:
        """Parse FAQs from a BeautifulSoup object"""
        faqs = []
        
        logger.info("Starting FAQ parsing with multiple methods")
        
        # Method 1: Look for accordion/collapsible structures
        def has_faq_class(css_class):
            if css_class is None:
                return False
            if isinstance(css_class, list):
                return any(any(term in str(c).lower() for term in ['accordion', 'faq', 'collaps', 'toggle']) for c in css_class)
            return any(term in str(css_class).lower() for term in ['accordion', 'faq', 'collaps', 'toggle'])
        
        accordion_items = soup.find_all(['div', 'section'], class_=has_faq_class)
        logger.info(f"Method 1 (accordion): Found {len(accordion_items)} potential accordion items")
        
        for item in accordion_items:
            def has_question_class(css_class):
                if css_class is None:
                    return False
                if isinstance(css_class, list):
                    return any(any(term in str(c).lower() for term in ['question', 'title', 'header', 'toggle']) for c in css_class)
                return any(term in str(css_class).lower() for term in ['question', 'title', 'header', 'toggle'])
            
            def has_answer_class(css_class):
                if css_class is None:
                    return False
                if isinstance(css_class, list):
                    return any(any(term in str(c).lower() for term in ['answer', 'content', 'body']) for c in css_class)
                return any(term in str(css_class).lower() for term in ['answer', 'content', 'body'])
            
            question_elem = item.find(['h3', 'h4', 'h5', 'button', 'summary'], class_=has_question_class)
            answer_elem = item.find(['div', 'p'], class_=has_answer_class)
            
            if question_elem and answer_elem:
                question = clean_text(question_elem.get_text())
                answer = clean_text(answer_elem.get_text())
                if question and answer:
                    faqs.append(FAQ(question=question, answer=answer))
                    logger.debug(f"Found FAQ (accordion): Q: {question[:50]}... A: {answer[:50]}...")
        
        # Method 2: Look for dt/dd pairs
        if not faqs:
            dt_elements = soup.find_all('dt')
            logger.info(f"Method 2 (dt/dd): Found {len(dt_elements)} dt elements")
            
            for dt in dt_elements:
                dd = dt.find_next_sibling('dd')
                if dd:
                    question = clean_text(dt.get_text())
                    answer = clean_text(dd.get_text())
                    if question and answer:
                        faqs.append(FAQ(question=question, answer=answer))
                        logger.debug(f"Found FAQ (dt/dd): Q: {question[:50]}... A: {answer[:50]}...")
        
        # Method 3: Look for h tags followed by paragraphs
        if not faqs:
            headers = soup.find_all(['h3', 'h4', 'h5'])
            logger.info(f"Method 3 (h tags): Found {len(headers)} headers")
            
            for header in headers:
                question_text = clean_text(header.get_text())
                if '?' in question_text:  # Likely a question
                    # Find the next paragraph or div
                    next_elem = header.find_next_sibling(['p', 'div'])
                    if next_elem:
                        answer_text = clean_text(next_elem.get_text())
                        if answer_text:
                            faqs.append(FAQ(question=question_text, answer=answer_text))
                            logger.debug(f"Found FAQ (h tags): Q: {question_text[:50]}... A: {answer_text[:50]}...")
        
        # Method 4: Look for common FAQ patterns in text
        if not faqs:
            logger.info("Method 4: Looking for common FAQ patterns in text")
            page_text = soup.get_text()
            
            # Look for patterns like "Q: ... A: ..." or "Question: ... Answer: ..."
            qa_patterns = [
                r'Q:\s*([^?]+\?)\s*A:\s*([^Q]+?)(?=Q:|$)',
                r'Question:\s*([^?]+\?)\s*Answer:\s*([^Q]+?)(?=Question:|$)',
                r'([^?]+\?)\s*([^?]+?)(?=[^?]+\?|$)'
            ]
            
            for pattern in qa_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if len(match) == 2:
                        question = clean_text(match[0].strip())
                        answer = clean_text(match[1].strip())
                        if question and answer and len(answer) > 10:  # Make sure answer is substantial
                            faqs.append(FAQ(question=question, answer=answer))
                            logger.debug(f"Found FAQ (pattern): Q: {question[:50]}... A: {answer[:50]}...")
        
        # Method 5: Look for list items that might be FAQs
        if not faqs:
            logger.info("Method 5: Looking for list items that might be FAQs")
            list_items = soup.find_all(['li', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['faq', 'question', 'help']))
            
            for item in list_items:
                text = clean_text(item.get_text())
                if '?' in text and len(text) > 20:  # Likely a question if it has ? and is long enough
                    # Try to split on question mark
                    parts = text.split('?', 1)
                    if len(parts) == 2:
                        question = clean_text(parts[0] + '?')
                        answer = clean_text(parts[1])
                        if question and answer and len(answer) > 5:
                            faqs.append(FAQ(question=question, answer=answer))
                            logger.debug(f"Found FAQ (list item): Q: {question[:50]}... A: {answer[:50]}...")
        
        logger.info(f"Total FAQs parsed: {len(faqs)}")
        
        # Remove duplicate FAQs based on question text
        unique_faqs = []
        seen_questions = set()
        
        for faq in faqs:
            # Normalize question for comparison (remove extra spaces, convert to lowercase)
            normalized_question = re.sub(r'\s+', ' ', faq.question.lower().strip())
            if normalized_question not in seen_questions:
                unique_faqs.append(faq)
                seen_questions.add(normalized_question)
        
        logger.info(f"After deduplication: {len(unique_faqs)} unique FAQs")
        return unique_faqs

    def extract_social_handles(self, website_url: str) -> List[SocialHandle]:
        """Extract social media handles from the website"""
        social_handles = []
        
        try:
            # Get the main page first
            response = self.session.get(website_url, timeout=self.timeout)
            if response.status_code != 200:
                return social_handles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            # Define social media platforms and their domains
            social_platforms = {
                'facebook': ['facebook.com', 'fb.com'],
                'instagram': ['instagram.com'],
                'twitter': ['twitter.com', 'x.com'],
                'tiktok': ['tiktok.com'],
                'youtube': ['youtube.com', 'youtu.be'],
                'linkedin': ['linkedin.com'],
                'pinterest': ['pinterest.com'],
                'snapchat': ['snapchat.com']
            }
            
            # Keep track of platforms we've already found to avoid duplicates
            found_platforms = set()
            
            logger.info(f"Found {len(links)} links to check for social media")
            
            for link in links:
                href_raw = link.get('href', '') if hasattr(link, 'get') else ''
                href = str(href_raw).lower() if href_raw else ''
                
                # Skip if this is a relative link or internal link
                if href.startswith('#') or href.startswith('/'):
                    continue
                
                for platform, domains in social_platforms.items():
                    # Only process if we haven't found this platform yet
                    if platform not in found_platforms and any(domain in href for domain in domains):
                        # Extract handle from URL
                        handle = self._extract_handle_from_url(href, platform)
                        
                        # Make sure we have a valid handle before adding
                        if handle and handle not in ['www', 'web', 'home']:
                            logger.info(f"Found {platform} handle: {handle} from URL: {href}")
                            social_handles.append(SocialHandle(
                                platform=platform,
                                url=href,
                                handle=handle
                            ))
                            found_platforms.add(platform)
                            break  # Move to next link once we find a platform
            
            logger.info(f"Extracted {len(social_handles)} social media handles: {[sh.platform for sh in social_handles]}")
        
        except Exception as e:
            logger.error(f"Error extracting social handles: {str(e)}")
        
        return social_handles

    def _extract_handle_from_url(self, url: str, platform: str) -> Optional[str]:
        """Extract handle/username from social media URL"""
        try:
            # Remove protocol and www
            clean_url = re.sub(r'^https?://(www\.)?', '', url)
            
            if platform == 'instagram':
                match = re.search(r'instagram\.com/([^/?]+)', clean_url)
                if match:
                    handle = match.group(1)
                    # Filter out common non-handle patterns
                    if handle not in ['www', 'web', 'home', 'explore', 'reels']:
                        return handle
            elif platform == 'facebook':
                match = re.search(r'facebook\.com/([^/?]+)', clean_url)
                if match:
                    handle = match.group(1)
                    # Filter out common non-handle patterns
                    if handle not in ['www', 'web', 'home', 'pages', 'groups']:
                        return handle
            elif platform in ['twitter', 'x']:
                match = re.search(r'(?:twitter|x)\.com/([^/?]+)', clean_url)
                if match:
                    handle = match.group(1)
                    # Filter out common non-handle patterns
                    if handle not in ['www', 'web', 'home', 'explore', 'notifications']:
                        return handle
            elif platform == 'tiktok':
                match = re.search(r'tiktok\.com/@([^/?]+)', clean_url)
                if match:
                    handle = match.group(1)
                    # Filter out common non-handle patterns
                    if handle not in ['www', 'web', 'home', 'explore']:
                        return handle
            elif platform == 'youtube':
                # YouTube can have channel URLs or video URLs
                if '/channel/' in clean_url:
                    match = re.search(r'youtube\.com/channel/([^/?]+)', clean_url)
                    if match:
                        return f"Channel: {match.group(1)[:20]}..."  # Truncate long channel IDs
                elif '/@' in clean_url:
                    match = re.search(r'youtube\.com/@([^/?]+)', clean_url)
                    if match:
                        return match.group(1)
                elif '/c/' in clean_url:
                    match = re.search(r'youtube\.com/c/([^/?]+)', clean_url)
                    if match:
                        return match.group(1)
            
            return None
        except Exception:
            return None

    def extract_contact_info(self, website_url: str) -> Optional[ContactInfo]:
        """Extract contact information from the website"""
        emails = []
        phone_numbers = []
        address = None
        
        # Check contact page first
        contact_paths = ['/pages/contact', '/contact', '/pages/contact-us', '/contact-us']
        
        for path in contact_paths:
            contact_url = urljoin(website_url, path)
            try:
                response = self.session.get(contact_url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text()
                    
                    # Extract emails
                    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                    emails.extend(email_matches)
                    
                    # Extract phone numbers
                    phone_matches = re.findall(r'[\+]?[\d\s\-\(\)]{10,}', page_text)
                    phone_numbers.extend([p.strip() for p in phone_matches if len(re.sub(r'\D', '', p)) >= 10])
                    
                    if emails or phone_numbers:
                        break
            except Exception as e:
                logger.debug(f"Error checking contact URL {contact_url}: {str(e)}")
        
        # If no contact page, check main page
        if not emails and not phone_numbers:
            try:
                response = self.session.get(website_url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text()
                    
                    # Extract emails
                    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                    emails.extend(email_matches)
                    
                    # Extract phone numbers (more restrictive for main page)
                    phone_matches = re.findall(r'[\+]?[\d\s\-\(\)]{10,}', page_text)
                    phone_numbers.extend([p.strip() for p in phone_matches if len(re.sub(r'\D', '', p)) >= 10])
            except Exception as e:
                logger.error(f"Error extracting contact info from main page: {str(e)}")
        
        # Clean and deduplicate
        emails = list(set([email.lower() for email in emails if '@' in email]))
        phone_numbers = list(set(phone_numbers))
        
        if emails or phone_numbers:
            return ContactInfo(
                emails=emails[:5],  # Limit to first 5 emails
                phone_numbers=phone_numbers[:3],  # Limit to first 3 phone numbers
                address=address
            )
        
        return None

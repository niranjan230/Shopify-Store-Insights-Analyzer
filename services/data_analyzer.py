import logging
from typing import Dict, List, Any
from models import BrandInsights
from datetime import datetime

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Service for analyzing and enhancing scraped data"""
    
    def analyze_brand_insights(self, insights: BrandInsights) -> Dict[str, Any]:
        """Analyze brand insights and return enhanced data with metrics"""
        analysis = {
            'basic_metrics': self._calculate_basic_metrics(insights),
            'content_quality': self._assess_content_quality(insights),
            'completeness_score': self._calculate_completeness_score(insights),
            'recommendations': self._generate_recommendations(insights)
        }
        
        return analysis
    
    def _calculate_basic_metrics(self, insights: BrandInsights) -> Dict[str, Any]:
        """Calculate basic metrics from the scraped data"""
        return {
            'total_products': len(insights.product_catalog),
            'hero_products_count': len(insights.hero_products),
            'faq_count': len(insights.faqs),
            'social_platforms': len(insights.social_handles),
            'contact_methods': (
                len(insights.contact_info.emails) + len(insights.contact_info.phone_numbers)
                if insights.contact_info else 0
            ),
            'important_links_count': len(insights.important_links),
            'has_privacy_policy': insights.privacy_policy_url is not None,
            'has_return_policy': insights.return_refund_policy_url is not None
        }
    
    def _assess_content_quality(self, insights: BrandInsights) -> Dict[str, Any]:
        """Assess the quality of extracted content"""
        quality_scores = {}
        
        # Brand description quality
        if insights.brand_description:
            desc_length = len(insights.brand_description)
            quality_scores['brand_description'] = 'good' if desc_length > 50 else 'basic'
        else:
            quality_scores['brand_description'] = 'missing'
        
        # Product catalog quality
        if insights.product_catalog:
            products_with_images = sum(1 for p in insights.product_catalog if p.images)
            products_with_prices = sum(1 for p in insights.product_catalog if p.price)
            total_products = len(insights.product_catalog)
            
            image_coverage = products_with_images / total_products if total_products > 0 else 0
            price_coverage = products_with_prices / total_products if total_products > 0 else 0
            
            quality_scores['product_catalog'] = {
                'image_coverage': f"{image_coverage:.2%}",
                'price_coverage': f"{price_coverage:.2%}",
                'overall': 'good' if image_coverage > 0.8 and price_coverage > 0.8 else 'basic'
            }
        else:
            quality_scores['product_catalog'] = 'missing'
        
        # FAQ quality
        if insights.faqs:
            avg_answer_length = sum(len(faq.answer) for faq in insights.faqs) / len(insights.faqs)
            quality_scores['faqs'] = 'good' if avg_answer_length > 30 else 'basic'
        else:
            quality_scores['faqs'] = 'missing'
        
        return quality_scores
    
    def _calculate_completeness_score(self, insights: BrandInsights) -> float:
        """Calculate a completeness score based on available data"""
        required_fields = [
            'brand_name',
            'product_catalog',
            'privacy_policy_url',
            'contact_info',
            'social_handles'
        ]
        
        score = 0
        total_weight = len(required_fields)
        
        for field in required_fields:
            value = getattr(insights, field, None)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    score += 1
                elif isinstance(value, str) and value.strip():
                    score += 1
                elif value is not None:
                    score += 1
        
        return score / total_weight
    
    def _generate_recommendations(self, insights: BrandInsights) -> List[str]:
        """Generate recommendations for improving data completeness"""
        recommendations = []
        
        if not insights.brand_name:
            recommendations.append("Brand name could not be extracted - check page title")
        
        if not insights.product_catalog:
            recommendations.append("No products found - verify /products.json endpoint")
        
        if not insights.privacy_policy_url:
            recommendations.append("Privacy policy not found - check common policy pages")
        
        if not insights.return_refund_policy_url:
            recommendations.append("Return/refund policy not found")
        
        if not insights.faqs:
            recommendations.append("No FAQs found - check for FAQ or help pages")
        
        if not insights.contact_info:
            recommendations.append("Contact information not found - check contact page")
        
        if not insights.social_handles:
            recommendations.append("No social media handles found")
        
        if len(insights.important_links) < 3:
            recommendations.append("Limited important links found - may need manual verification")
        
        return recommendations
    
    def format_insights_for_response(self, insights: BrandInsights) -> Dict[str, Any]:
        """Format insights data for JSON response"""
        return {
            'website_url': insights.website_url,
            'brand_name': insights.brand_name,
            'brand_description': insights.brand_description,
            'scraped_at': insights.scraped_at.isoformat() if insights.scraped_at else None,
            'product_catalog': [
                {
                    'id': p.id,
                    'title': p.title,
                    'handle': p.handle,
                    'description': p.description[:200] + '...' if p.description and len(p.description) > 200 else p.description,
                    'vendor': p.vendor,
                    'product_type': p.product_type,
                    'price': p.price,
                    'compare_at_price': p.compare_at_price,
                    'available': p.available,
                    'tags': p.tags,
                    'images': p.images[:3] if p.images else [],  # Limit to 3 images
                    'url': p.url
                }
                for p in insights.product_catalog
            ],
            'hero_products': [
                {
                    'title': p.title,
                    'price': p.price,
                    'images': p.images[:2] if p.images else [],  # Limit to 2 images
                    'url': p.url
                }
                for p in insights.hero_products
            ],
            'privacy_policy': {
                'url': insights.privacy_policy_url,
                'content_preview': insights.privacy_policy_content[:300] + '...' if insights.privacy_policy_content and len(insights.privacy_policy_content) > 300 else insights.privacy_policy_content
            },
            'return_refund_policy': {
                'url': insights.return_refund_policy_url,
                'content_preview': insights.return_refund_policy_content[:300] + '...' if insights.return_refund_policy_content and len(insights.return_refund_policy_content) > 300 else insights.return_refund_policy_content
            },
            'faqs': [
                {
                    'question': faq.question,
                    'answer': faq.answer,
                    'category': faq.category
                }
                for faq in insights.faqs
            ],
            'social_handles': [
                {
                    'platform': handle.platform,
                    'url': handle.url,
                    'handle': handle.handle
                }
                for handle in insights.social_handles
            ],
            'contact_info': {
                'emails': insights.contact_info.emails,
                'phone_numbers': insights.contact_info.phone_numbers,
                'address': insights.contact_info.address
            } if insights.contact_info else None,
            'important_links': insights.important_links
        }

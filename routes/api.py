from flask import Blueprint, request, jsonify
import logging
from pydantic import ValidationError
from schemas.brand_data import WebsiteUrlRequest
from services.shopify_scraper import ShopifyScraper
from services.data_analyzer import DataAnalyzer
from utils.validators import validate_shopify_url
import traceback

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze_shopify_store():
    """Main API endpoint to analyze a Shopify store"""
    try:
        # Validate request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                'error': 'JSON request body required',
                'status_code': 400
            }), 400
        
        # Validate using Pydantic schema
        try:
            validated_data = WebsiteUrlRequest(**request_data)
            website_url = validated_data.website_url
        except ValidationError as e:
            return jsonify({
                'error': 'Invalid request data',
                'details': e.errors(),
                'status_code': 400
            }), 400
        
        # Additional URL validation
        if not validate_shopify_url(website_url):
            return jsonify({
                'error': 'Invalid or inaccessible website URL',
                'status_code': 401
            }), 401
        
        logger.info(f"Starting analysis for URL: {website_url}")
        
        # Initialize scraper and analyzer
        scraper = ShopifyScraper()
        analyzer = DataAnalyzer()
        
        # Scrape the store
        try:
            insights = scraper.scrape_store(website_url)
        except Exception as e:
            logger.error(f"Scraping failed for {website_url}: {str(e)}")
            error_msg = str(e)
            
            if "not accessible" in error_msg.lower() or "not found" in error_msg.lower():
                return jsonify({
                    'error': 'Website not found or not accessible',
                    'status_code': 401
                }), 401
            else:
                return jsonify({
                    'error': 'Internal server error during scraping',
                    'details': error_msg,
                    'status_code': 500
                }), 500
        
        # Analyze and format the data
        formatted_insights = analyzer.format_insights_for_response(insights)
        analysis_metrics = analyzer.analyze_brand_insights(insights)
        
        # Prepare response
        response_data = {
            'success': True,
            'data': formatted_insights,
            'analysis': analysis_metrics,
            'status_code': 200
        }
        
        logger.info(f"Successfully analyzed store: {website_url}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze_shopify_store: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'details': 'An unexpected error occurred while processing your request',
            'status_code': 500
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Shopify Insights API is running',
        'timestamp': '2024-08-16T00:00:00Z'
    }), 200

@api_bp.route('/validate-url', methods=['POST'])
def validate_url():
    """Endpoint to validate if a URL is a valid Shopify store"""
    try:
        request_data = request.get_json()
        if not request_data or 'website_url' not in request_data:
            return jsonify({
                'error': 'website_url field required',
                'status_code': 400
            }), 400
        
        website_url = request_data['website_url']
        is_valid = validate_shopify_url(website_url)
        
        return jsonify({
            'website_url': website_url,
            'is_valid_shopify_store': is_valid,
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error in validate_url: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'error': 'API endpoint not found',
        'status_code': 404
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'status_code': 405
    }), 405

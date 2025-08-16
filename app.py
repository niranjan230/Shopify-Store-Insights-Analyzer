import os
import logging
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for API calls
CORS(app)

# App config
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

# Import and register blueprints
from routes.api import api_bp
from flask import render_template

app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Show the main page"""
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found', 'status_code': 404}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return {'error': 'Internal server error', 'status_code': 500}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

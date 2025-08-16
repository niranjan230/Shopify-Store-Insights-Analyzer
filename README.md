# Shopify Store Insights Analyzer

A web app that gets comprehensive brand intelligence from Shopify stores by just entering a store URL. No official APIs needed - just put in a Shopify store URL and get detailed insights right away.

## What it does

- **Product Catalog Analysis**: Gets the full list of products with prices and images
- **Brand Intelligence**: Collects brand info and descriptions
- **Policy Extraction**: Finds and extracts privacy and return policies automatically
- **FAQ Discovery**: Identifies and extracts frequently asked questions
- **Social Media Integration**: Finds social media handles and links
- **Contact Information**: Gets emails, phone numbers, and addresses
- **Important Links**: Discovers order tracking, contact forms, and other key pages

## Tech stack

- **Backend**: Python 3.11+, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Processing**: BeautifulSoup4, Trafilatura, Pydantic
- **HTTP Client**: Requests with retry logic and rate limiting
- **Data Models**: Python dataclasses with type hints

## How to set it up

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to use it

1. Start the app:
   ```bash
   python main.py
   ```
2. Open your browser and go to `http://localhost:5000`
3. **Enter any Shopify store URL** (e.g., memy.co.in, hairoriginals.com, or any .myshopify.com domain)
4. Click "Analyze Store" to get instant brand insights

## API endpoints

- `POST /api/analyze` - Main analysis endpoint
- `POST /api/validate-url` - URL validation endpoint
- `GET /api/health` - Health check endpoint

## Project structure

```
├── app.py                 # Flask app setup
├── main.py               # Entry point
├── models.py             # Data models
├── routes/               # API routes
├── services/             # Core logic
├── schemas/              # Data validation
├── utils/                # Helper functions
├── templates/            # HTML templates
└── static/               # CSS, JS, and static files
```

## Main components

- **ShopifyScraper**: Main scraping service with retry logic
- **DataAnalyzer**: Data processing and formatting
- **ContentExtractor**: Content extraction utilities
- **Validators**: Input validation

## Key features

- Retry logic with exponential backoff
- Rate limiting protection
- Good error handling
- Clean, maintainable code
- Type hints throughout
- Proper logging

## License

This project is for educational and demo purposes.

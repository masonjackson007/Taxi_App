from flask import Flask
import logging
from services.filter_service import FilterService

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/test')
def test_endpoint():
    logger.info("Test endpoint was called")
    return {"message": "Test successful"}

@app.route('/api/filters', methods=['GET'])
def get_filter_options():
    logger.info("Filter options endpoint called")
    
    filter_service = FilterService()
    filter_options = filter_service.get_available_filters()
    
    if filter_options is None:
        logger.error("Failed to get filter options")
        return {"error": "Failed to get filter options"}, 500
        
    logger.info("Successfully retrieved filter options")
    return filter_options

@app.route('/api/report', methods=['POST'])
def generate_report():
    # Generate report based on selected filters
    pass

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000)
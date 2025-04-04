from flask import Flask, request, jsonify
import logging
from services.filter_service import FilterService
from services.data_service import DataService

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

@app.route('/api/timeseries', methods=['POST'])
def generate_timeseries():
    try:
        # Get filter parameters from request
        filters = request.get_json()
        
        # Validate date range parameters
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        if not start_date or not end_date:
            logger.error("Missing required date parameters")
            return jsonify({
                "error": "Missing required date range parameters"
            }), 400
            
        # Get passenger counts filter if provided
        passenger_counts = filters.get('passenger_counts')
        
        # Get distance range filters if provided
        min_distance = filters.get('min_distance')
        max_distance = filters.get('max_distance')
            
        # Initialize data service
        data_service = DataService()
        
        # Get filtered data and analysis
        result = data_service.analyze_timeseries(
            start_date, 
            end_date, 
            passenger_counts,
            min_distance,
            max_distance
        )
        
        if result is None:
            logger.error("Failed to generate time series analysis")
            return jsonify({
                "error": "Failed to generate time series analysis"
            }), 500
            
        if "error" in result:
            logger.warning(f"Time series analysis returned error: {result['error']}")
            return jsonify(result), 404
            
        logger.info("Successfully generated time series analysis")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating time series: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000)
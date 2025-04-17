from flask import Flask, request, jsonify
import logging
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from services.filter_service import FilterService
from services.data_service import DataService
from services.auth_service import AuthService
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Backend starting up")

app = Flask(__name__)

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

# Initialize database
try:
    with app.app_context():
        init_db()
        logger.info("Database initialized")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")

@app.route('/test')
def test_endpoint():
    logger.info("Test endpoint was called")
    return {"message": "Test successful"}

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "error": "Email and password are required"
            }), 400
            
        email = data.get('email')
        password = data.get('password')
        
        # Register user
        auth_service = AuthService()
        success, message, user_id = auth_service.register_user(email, password)
        
        if success:
            return jsonify({
                "message": message,
                "user_id": user_id
            }), 201
        else:
            return jsonify({
                "error": message
            }), 400
            
    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return jsonify({
            "error": "Registration failed"
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "error": "Email and password are required"
            }), 400
            
        email = data.get('email')
        password = data.get('password')
        
        # Authenticate user
        auth_service = AuthService()
        success, message, token = auth_service.authenticate_user(email, password)
        
        if success:
            return jsonify({
                "message": message,
                "access_token": token
            }), 200
        else:
            return jsonify({
                "error": message
            }), 401
            
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({
            "error": "Login failed"
        }), 500

@app.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        user_identity = get_jwt_identity()
        user_id = user_identity.get('user_id')
        
        # Get user info
        auth_service = AuthService()
        user_info = auth_service.get_user_by_id(user_id)
        
        if user_info:
            return jsonify(user_info), 200
        else:
            return jsonify({
                "error": "User not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_user endpoint: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve user information"
        }), 500

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
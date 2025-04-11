import requests
import streamlit as st
import os
import logging
import jwt
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:5000/api")

def register_user(email, password):
    """
    Register a new user via the backend API.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Tuple of (success, message)
    """
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/auth/register",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 201:
            logger.info(f"Successfully registered user: {email}")
            return True, "Registration successful"
        else:
            error_msg = response.json().get("error", "Unknown error")
            logger.warning(f"Registration failed for {email}: {error_msg}")
            return False, f"Registration failed: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during registration: {str(e)}")
        return False, f"Connection error: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return False, f"Unexpected error: {str(e)}"

def login_user(email, password):
    """
    Authenticate user and save JWT token in session state.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Tuple of (success, message)
    """
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if not token:
                logger.error("Login response missing access token")
                return False, "Invalid response from server"
                
            # Store token in session state
            st.session_state.jwt_token = token
            st.session_state.logged_in = True
            
            # Try to get user details from token
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                if "identity" in decoded:
                    st.session_state.user_email = decoded["identity"].get("email")
            except Exception as e:
                logger.warning(f"Error decoding JWT token: {str(e)}")
            
            logger.info(f"Successfully logged in user: {email}")
            return True, "Login successful"
        else:
            error_msg = response.json().get("error", "Invalid credentials")
            logger.warning(f"Login failed for {email}: {error_msg}")
            return False, f"Login failed: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during login: {str(e)}")
        return False, f"Connection error: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return False, f"Unexpected error: {str(e)}"

def logout_user():
    """Log out the current user by clearing session state."""
    if "jwt_token" in st.session_state:
        del st.session_state.jwt_token
    if "logged_in" in st.session_state:
        del st.session_state.logged_in
    if "user_email" in st.session_state:
        del st.session_state.user_email
    logger.info("User logged out")

def is_authenticated():
    """Check if user is authenticated with a valid token."""
    if not st.session_state.get("logged_in", False) or not st.session_state.get("jwt_token"):
        return False
        
    # Check if token is expired
    try:
        token = st.session_state.jwt_token
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded.get("exp")
        
        if not exp_timestamp:
            logger.warning("Token missing expiration")
            return False
            
        # Check if token is expired
        expiration = datetime.fromtimestamp(exp_timestamp)
        if expiration < datetime.now():
            logger.info("Token expired, logging out")
            logout_user()
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return False

def get_current_user():
    """Get current user information from the backend."""
    if not is_authenticated():
        return None
        
    try:
        headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
        response = requests.get(
            f"{BACKEND_API_URL}/auth/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to get user info: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return None 
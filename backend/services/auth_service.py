import logging
from flask_jwt_extended import create_access_token, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from models.user_model import User
from database import get_db

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.db = get_db()
    
    def register_user(self, email, password):
        """
        Register a new user with email and password.
        Returns tuple (success, message, user_id)
        """
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {email}")
                return False, "Email already registered", None
            
            # Create new user
            new_user = User(email=email, password=password)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"Successfully registered new user: {email}")
            return True, "Registration successful", new_user.id
            
        except IntegrityError as e:
            logger.error(f"Database integrity error during registration: {str(e)}")
            self.db.rollback()
            return False, "Registration failed - database error", None
            
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            self.db.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    def authenticate_user(self, email, password):
        """
        Authenticates a user and returns JWT token if successful.
        Returns tuple (success, message, token)
        """
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == email).first()
            
            # If user not found or password incorrect
            if not user or not user.check_password(password):
                logger.warning(f"Failed login attempt for email: {email}")
                return False, "Invalid email or password", None
            
            # If user account is inactive
            if not user.is_active:
                logger.warning(f"Login attempt for inactive account: {email}")
                return False, "Account is inactive", None
            
            # Generate access token
            access_token = create_access_token(
                identity={"user_id": user.id, "email": user.email},
                expires_delta=timedelta(days=1)
            )
            
            logger.info(f"Successful login for user: {email}")
            return True, "Login successful", access_token
            
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False, f"Authentication error: {str(e)}", None
    
    def get_user_by_id(self, user_id):
        """Get user information by ID."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
                
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
            return None 
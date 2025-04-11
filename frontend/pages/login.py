import streamlit as st
import re
from services.auth_service import register_user, login_user, is_authenticated, logout_user

# Set page config
st.set_page_config(
    page_title="Taxi Dashboard - Login",
    layout="centered",
)

# Initialize session state variables if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_register_form" not in st.session_state:
    st.session_state.show_register_form = False

# Email validation function
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

# Password validation function
def is_valid_password(password):
    # At least 8 characters, containing at least one number and one letter
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    return True, ""

def show_login_form():
    # Login form
    st.header("Login")
    
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", type="primary"):
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        success, message = login_user(email, password)
        if success:
            st.success(message)
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error(message)
    
    st.divider()
    
    # Switch to registration form
    if st.button("Don't have an account? Register here"):
        st.session_state.show_register_form = True
        st.rerun()

def show_register_form():
    # Registration form
    st.header("Register")
    
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    
    if st.button("Register", type="primary"):
        # Validate inputs
        if not email or not password or not confirm_password:
            st.error("Please fill in all fields")
            return
            
        if not is_valid_email(email):
            st.error("Please enter a valid email address")
            return
            
        is_valid, password_error = is_valid_password(password)
        if not is_valid:
            st.error(password_error)
            return
            
        if password != confirm_password:
            st.error("Passwords do not match")
            return
            
        # Register user
        success, message = register_user(email, password)
        if success:
            st.success(f"{message} Please log in.")
            st.session_state.show_register_form = False
            st.rerun()
        else:
            st.error(message)
    
    st.divider()
    
    # Switch back to login form
    if st.button("Already have an account? Login here"):
        st.session_state.show_register_form = False
        st.rerun()

def show_logged_in_view():
    st.header("You are logged in")
    st.write(f"Welcome")
    
    if st.button("Go to Dashboard"):
        st.switch_page("frontend.py")
        
    if st.button("Log Out"):
        logout_user()
        st.session_state.logged_in = False
        st.rerun()

# Main page content
st.title("Taxi Trip Dashboard")

# Show appropriate form based on state
if is_authenticated():
    show_logged_in_view()
elif st.session_state.show_register_form:
    show_register_form()
else:
    show_login_form() 
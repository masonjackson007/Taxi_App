import streamlit as st
from services.auth_service import is_authenticated, logout_user

def render_header():
    """
    Renders the application header with authentication status
    and navigation links. This component should be added to
    all pages at the top.
    """

    with st.container():
        cols = st.columns([3, 1])
        
        # Left column App title
        with cols[0]:
            st.markdown("### Taxi Trip Dashboard")
        
        # Right column User info and buttons
        with cols[1]:
            if is_authenticated():
                # User is logged in show logout button
                user_email = st.session_state.get("user_email", "User")
                st.text(f"Logged in")
                
                if st.button("Log Out", key="header_logout"):
                    logout_user()
                    # Redirect to the login page
                    st.switch_page("pages/login.py")
            else:
                # User is not logged in show login button
                if st.button("Log In", key="header_login"):
                    st.switch_page("pages/login.py")
        
        st.divider() 
import streamlit as st
import os
from components.header import render_header

# Set page title
st.set_page_config(
    page_title="Taxi Data Dashboard - Documentation",
    layout="wide"
)

# Render header component
render_header()

st.title("Taxi Data Dashboard - Documentation")

# Path to the documentation markdown file
documentation_path = os.path.join(os.path.dirname(__file__), "documentation.md")

# Read the markdown file content
try:
    with open(documentation_path, "r") as file:
        documentation_content = file.read()
    
    # Display the markdown content
    st.markdown(documentation_content)
except FileNotFoundError:
    st.error(f"Documentation file not found")
except Exception as e:
    st.error(f"Error loading documentation")
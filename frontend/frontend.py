# Taxi_App/frontend/frontend.py
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd
import logging
from services.api_client import fetch_filter_options, fetch_timeseries_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


st.set_page_config(
    page_title="Taxi Trip Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper Function for Date Conversion
def parse_api_date(date_str: str) -> date | None:
    """Safely parses ISO date string from API to date object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.split('T')[0]).date()
    except (ValueError, TypeError):
        logger.warning(f"Could not parse date string: {date_str}")
        return None

# Function to Fetch Initial Filter Options
# Use cache to avoid refetching on every interaction
@st.cache_data(ttl=3600) # Cache for 1 hour
def load_filter_options():
    """Fetches filter options from the backend and caches them."""
    logger.info("Attempting to load filter options.")
    try:
        options = fetch_filter_options()
        # validation of received options
        if not options or 'date_range' not in options or \
           'min_date' not in options['date_range'] or \
           'max_date' not in options['date_range']:
             logger.error(f"Invalid filter options received: {options}")
             raise ApiClientError("Received invalid filter options structure from backend.")
        return options
    except ApiClientError as e:
        logger.error(f"Failed to load filter options: {e}")
        st.error(f"Could not load filter options from backend: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading filter options: {e}")
        st.error(f"An unexpected error occurred while loading filter options: {e}")
        return None

# Main App Logic
st.title("Taxi Trip Time Series Analysis")
st.write("Use the filters in the sidebar to select the data range and view the analysis.")

# Load Filter Options
filter_options = load_filter_options()

# If filter options failed to load, stop the script
if filter_options is None:
    st.warning("Dashboard cannot be displayed because filter options could not be loaded.")
    st.stop() 

# Extract Date Range
try:
    min_available_date = parse_api_date(filter_options['date_range']['min_date'])
    max_available_date = parse_api_date(filter_options['date_range']['max_date'])

    if not min_available_date or not max_available_date:
        raise ValueError("Min or Max date could not be parsed from API response.")


except (KeyError, ValueError, TypeError) as e:
    logger.error(f"Error processing date range from filter_options: {e} - Options: {filter_options}")
    st.error(f"Error processing available date range from backend. Details: {e}")

# Sidebar Filters
st.sidebar.header("Filters")

selected_start_date = st.sidebar.date_input(
    "Start Date",
    min_value=min_available_date,
    max_value=max_available_date
)

selected_end_date = st.sidebar.date_input(
    "End Date",
    min_value=min_available_date, 
    max_value=max_available_date
)

# Function to Process API Data into DataFrame and Stats 
def process_api_response(api_data: dict) -> tuple[pd.DataFrame | None, dict | None]:
    """
    Processes the raw API response data into a pandas DataFrame and extracts statistics.

    Args:
        api_data: The dictionary response from the backend API.

    Returns:
        A tuple containing (DataFrame, statistics_dict).
        Returns (None, None) if processing fails.
    """
    try:
        data_points = api_data['data_points']
        stats = api_data.get('summary_statistics', {})

        df = pd.DataFrame({
            'Date': pd.to_datetime(data_points['dates']),
            'Trips': data_points['trip_counts'],
            'Passengers': data_points['passenger_counts'],
            'Average Distance': data_points['average_distances'],
            'Revenue': data_points['daily_revenue']
        })
        df.set_index('Date', inplace=True)
        logger.info("Successfully processed API data into DataFrame.")
        return df, stats
    
    except KeyError as e:
        logger.error(f"KeyError processing API data: Missing key {e}. Data: {api_data}")
        st.error(f"Error processing API data: Missing expected key '{e}'. Check the API response structure.")
        st.json(api_data) 
        return None, None
    
    except Exception as e:
        logger.error(f"Unexpected error processing data: {e}. Data: {api_data}")
        st.error(f"An unexpected error occurred while processing data: {e}")
        st.json(api_data)
        return None, None

# Function to Display Summary Statistics
def display_summary_statistics(stats: dict):
    """Displays summary statistics using st.metric in columns."""
    st.markdown("#### Summary Statistics")
    if not stats:
        st.warning("Summary statistics not found or empty in the API response.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Trips", f"{stats.get('total_trips', 'N/A'):,}")
        st.metric("Total Passengers", f"{stats.get('total_passengers', 'N/A'):,}")
    with col2:
        st.metric("Avg Daily Trips", f"{stats.get('average_daily_trips', 0):.2f}")
        st.metric("Avg Trip Distance (miles)", f"{stats.get('average_trip_distance', 0):.2f}")
    with col3:
        st.metric("Total Revenue", f"${stats.get('total_revenue', 0):,.2f}")
        st.metric("Avg Daily Revenue", f"${stats.get('average_daily_revenue', 0):,.2f}")

# Function to Display Time Series Plots
def display_time_series_plots(df: pd.DataFrame):
    """Displays the time series plots for trips/passengers and revenue."""
    if df is None or df.empty:
        st.warning("No data points available to plot for the selected range.")
        return

    st.markdown("#### Time Series Plots")

    # Plot Trips and Passengers
    try:
        fig_trips_pass = px.line(df, y=['Trips', 'Passengers'],
                                title='Daily Trips and Passengers',
                                labels={'value': 'Count', 'variable': 'Metric'},
                                markers=True)
        fig_trips_pass.update_layout(hovermode="x unified")
        st.plotly_chart(fig_trips_pass, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating Trips/Passengers plot: {e}")
        st.error(f"Could not display Trips/Passengers plot. Error: {e}")


    # Plot Revenue
    try:
        fig_revenue = px.line(df, y='Revenue',
                              title='Daily Revenue',
                              labels={'Revenue': 'Revenue ($)'},
                              markers=True)
        fig_revenue.update_layout(hovermode="x unified")
        st.plotly_chart(fig_revenue, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating Revenue plot: {e}")
        st.error(f"Could not display Revenue plot. Error: {e}")


    # Display the raw data in an expander
    with st.expander("View Raw Data Table"):
        st.dataframe(df)

if st.sidebar.button("Analyze Data", type="primary"):

    # Input Validation
    if selected_start_date > selected_end_date:
        st.error("Error: Start date cannot be after end date.")
    else:
        st.markdown("---")
        st.subheader(f"Analysis Results: {selected_start_date.strftime('%Y-%m-%d')} to {selected_end_date.strftime('%Y-%m-%d')}")

        # Show a spinner while fetching data
        with st.spinner(f"Fetching and analyzing data from {selected_start_date} to {selected_end_date}..."):
            try:
                # Fetch Data
                api_data = fetch_timeseries_data(selected_start_date, selected_end_date)

                # Process Data 
                df, stats = process_api_response(api_data)

                # Display Results
                if df is not None and stats is not None:
                    display_summary_statistics(stats)
                    display_time_series_plots(df)

                    # Show filter info from response
                    filter_info = api_data.get('filter_info')
                    if filter_info:
                        st.caption(f"Analysis based on {filter_info.get('total_days', 'N/A')} days of data within the selected range.")
                else:
                    st.warning("Analysis could not be completed due to data processing errors. See messages above.")

            except ApiClientError as e:
                logger.error(f"API Client Error on analyze: {e}")
                st.error(f"Failed to fetch data from the backend: {e}")
                st.info("Please ensure the backend service is running and check its logs for more details.")
            except Exception as e:
                logger.exception(f"An unexpected error occurred during analysis: {e}") 
                st.error(f"An unexpected error occurred: {e}")

else:
    # Message shown before the button is clicked
    st.info("Adjust the date range in the sidebar and click 'Analyze Data' to load the analysis.")


st.sidebar.markdown("---")

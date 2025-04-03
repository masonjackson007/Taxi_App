import requests
import streamlit as st
import os
from datetime import date
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Define the base URL for the backend API
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:5000/api")
logger.info(f"Backend API URL set to: {BACKEND_API_URL}")


def make_request(method: str, endpoint: str, **kwargs) -> dict:
    """Helper function to make requests and handle common errors."""
    url = f"{BACKEND_API_URL}/{endpoint}"
    logger.info(f"Making {method} request to {url} with params: {kwargs.get('params', kwargs.get('json', 'N/A'))}")
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        response.raise_for_status() 

        if "application/json" not in response.headers.get("Content-Type", ""):
            logger.error(f"Unexpected content type received from {url}: {response.headers.get('Content-Type', 'N/A')}")
            raise ApiClientError(f"Unexpected content type: {response.headers.get('Content-Type', 'N/A')}. Expected JSON.")

        data = response.json()
        logger.info(f"Successfully received JSON response from {url}")
        return data

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err}"
        try:
            # Try to get more specific error from API response body
            error_detail = response.json().get('error', f'Status Code: {response.status_code}')
            error_message = f"API Error ({response.status_code}): {error_detail}"
            logger.error(f"API Error from {url}: {error_message} - Response: {response.text}")
        except Exception:
            # Keep original HTTP error message if response is not JSON
            logger.error(f"HTTP Error from {url}: {http_err} - Response: {response.text}")
            pass 
        raise ApiClientError(error_message) from http_err

    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection Error connecting to {url}: {conn_err}")
        raise ApiClientError(f"Connection Error: Could not connect to the backend at {url}. Ensure the backend service is running and accessible.") from conn_err

    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Request timed out connecting to {url}: {timeout_err}")
        raise ApiClientError(f"Request timed out connecting to {url}.") from timeout_err

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception for {url}: {req_err}")
        raise ApiClientError(f"An unexpected error occurred during the API request: {req_err}") from req_err

    except Exception as e:
        logger.error(f"An unexpected error occurred processing request to {url}: {e}")
        raise ApiClientError(f"An unexpected error occurred: {str(e)}")


def fetch_filter_options() -> dict:
    """
    Fetches available filter options (date range, passenger counts, etc.)
    from the backend API.

    Returns:
        A dictionary containing the filter options.

    Raises:
        ApiClientError: If the API request fails or returns an error status.
    """
    logger.info("Attempting to fetch filter options.")
    return make_request("GET", "filters")


def fetch_timeseries_data(start_date: date, end_date: date, passenger_counts: list = None) -> dict:
    """
    Fetches time series data from the backend API based on dates and passenger counts.

    Args:
        start_date: The start date for the analysis.
        end_date: The end date for the analysis.
        passenger_counts: Optional list of passenger count values to filter by.

    Returns:
        A dictionary containing the API response data.

    Raises:
        ApiClientError: If the API request fails or returns an error status.
    """
    logger.info(f"Attempting to fetch time series data from {start_date} to {end_date} with passenger counts: {passenger_counts}.")
    payload = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    # Add passenger counts filter if provided
    if passenger_counts is not None:
        payload["passenger_counts"] = passenger_counts
        
    return make_request("POST", "timeseries", json=payload)
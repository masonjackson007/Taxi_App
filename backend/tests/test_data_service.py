import pytest
import pandas as pd
from pathlib import Path
from services.data_service import DataService

@pytest.fixture
def data_service():
    """Provides a fresh instance of DataService for each test"""
    service = DataService()
    service.data_path = "/Taxi_App/data/taxi_data_mockup.parquet"
    return service

def test_successful_data_load(data_service):
    """Test that data loads successfully with valid file"""
    # Attempt to load data
    result = data_service.load_data()
    
    # Verify load was successful
    assert result is True
    assert data_service.df is not None
    
    # Verify expected columns exist
    expected_columns = ['tpep_pickup_datetime', 
                        'passenger_count', 
                        'trip_distance', 
                        'total_amount']
    for col in expected_columns:
        assert col in data_service.df.columns

def test_file_not_found(data_service):
    """Test behavior when file doesn't exist"""
    data_service.data_path = "fake_file.parquet"
    result = data_service.load_data()
    assert result is False

def test_successful_timeseries_analysis(data_service):
    """Test time series analysis with valid date range"""
    # First load the data
    data_service.load_data()
    
    # Get the actual date range from the mock data
    min_date = data_service.df['tpep_pickup_datetime'].min().strftime('%Y-%m-%d')
    max_date = data_service.df['tpep_pickup_datetime'].max().strftime('%Y-%m-%d')
    
    # Perform analysis
    result = data_service.analyze_timeseries(min_date, max_date)
    
    # Verify response structure
    assert result is not None
    assert "data_points" in result
    assert "summary_statistics" in result
    assert "filter_info" in result

def test_invalid_date_range(data_service):
    """Test when start date is after end date"""
    data_service.load_data()
    result = data_service.analyze_timeseries("2025-02-01", "2025-01-01")
    
    assert result is not None
    assert "error" in result
    assert "Start date must be before end date" in result["error"]

def test_dates_outside_available_range(data_service):
    """Test dates outside the available data range"""
    data_service.load_data()
    result = data_service.analyze_timeseries("2026-01-01", "2026-02-01")
    
    assert result is not None
    assert "error" in result
    assert "Date range must be between" in result["error"]
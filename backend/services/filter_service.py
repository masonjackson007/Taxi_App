import logging
import pandas as pd
import pyarrow
from pathlib import Path

class FilterService:
    def __init__(self):
        self.data = None
        self.data_path = "/Taxi_App/data/yellow_tripdata_2025-01_cleaned_optimized.parquet"
        self.logger = logging.getLogger(__name__)

    def load_data(self):
        # Load parquet data file
        try:
            file_path = Path(self.data_path)
            if not file_path.exists():
                self.logger.error(f"Data file not found at {self.data_path}")
                return False
            
            self.logger.info(f"Loading data from {self.data_path}")
            self.data = pd.read_parquet(self.data_path)
            
            if self.data.empty:
                self.logger.error("Loaded data is empty")
                return False
                
            self.logger.info(f"Successfully loaded data with {len(self.data)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False

    def get_date_range(self):
        # Extract the minimum and maximum dates from the data
        if self.data is None:
            self.logger.error("Data not loaded. Call load_data() first")
            return None
            
        try:
            min_date = self.data['tpep_pickup_datetime'].min()
            max_date = self.data['tpep_pickup_datetime'].max()
            
            self.logger.info(f"Date range found: {min_date} to {max_date}")
            return {
                'min_date': min_date.isoformat(),
                'max_date': max_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting date range: {str(e)}")
            return None

    def get_available_filters(self):
        # Get all available filter options
        if not self.load_data():
            return None
            
        date_range = self.get_date_range()
        if not date_range:
            return None
            
        return {
            'date_range': date_range
        }
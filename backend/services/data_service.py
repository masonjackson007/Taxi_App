import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

class DataService:
    def __init__(self):
        self.df = None  # pandas DataFrame
        self.data_path = "/Taxi_App/data/yellow_tripdata_2025-01_cleaned_optimized.parquet"
        self.logger = logging.getLogger(__name__)
    
    def load_data(self):
        try:
            file_path = Path(self.data_path)
            if not file_path.exists():
                self.logger.error(f"Data file not found at {self.data_path}")
                return False
            
            self.logger.info(f"Loading data from {self.data_path}")
            self.df = pd.read_parquet(self.data_path)
            
            # Validate expected columns and types
            expected_columns = {
                'tpep_pickup_datetime': 'datetime64[us]',
                'passenger_count': 'UInt8',
                'trip_distance': 'float32',
                'total_amount': 'float32'
            }
            
            for col, dtype in expected_columns.items():
                if col not in self.df.columns:
                    self.logger.error(f"Required column {col} not found in data")
                    return False
                if str(self.df[col].dtype) != dtype:
                    self.logger.warning(f"Column {col} has unexpected dtype: {self.df[col].dtype}, expected: {dtype}")
            
            if self.df.empty:
                self.logger.error("Loaded data is empty")
                return False
                
            self.logger.info(f"Successfully loaded data with {len(self.df)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def get_available_filters(self):
        # Return unique dates, passenger counts, distance range
        pass
    
    def filter_data(self, filter_params):
        # Apply filters and return filtered DataFrame
        pass
    
    def generate_summary_stats(self, filtered_data):
        # Calculate summary statistics
        pass
    
    def generate_visualizations(self, filtered_data):
        # Create graphs/charts
        pass

    def analyze_timeseries(self, start_date, end_date, passenger_counts=None):
        """
        Analyze trip data within the specified date range and passenger counts and return time series data
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            passenger_counts: Optional list of passenger count values to filter by
        """
        try:
            # Load data if not already loaded
            if self.df is None and not self.load_data():
                return None

            # Convert string dates to datetime64[us] to match DataFrame type
            try:
                start_dt = pd.to_datetime(start_date).tz_localize(None)
                end_dt = pd.to_datetime(end_date).tz_localize(None)
            except Exception as e:
                self.logger.error(f"Invalid date format: {str(e)}")
                return {
                    "error": "Invalid date format. Please use YYYY-MM-DD format."
                }

            # Validate date range
            data_start = self.df['tpep_pickup_datetime'].min()
            data_end = self.df['tpep_pickup_datetime'].max()
            
            if start_dt > end_dt:
                return {
                    "error": "Start date must be before end date"
                }
            
            if end_dt < data_start or start_dt > data_end:
                return {
                    "error": f"Date range must be between {data_start.strftime('%Y-%m-%d')} and {data_end.strftime('%Y-%m-%d')}"
                }

            # Filter data by date range
            mask = (self.df['tpep_pickup_datetime'] >= start_dt) & (self.df['tpep_pickup_datetime'] <= end_dt)
            
            # Apply passenger count filter if provided
            if passenger_counts and len(passenger_counts) > 0:
                self.logger.info(f"Filtering by passenger counts: {passenger_counts}")
                mask = mask & (self.df['passenger_count'].isin(passenger_counts))
            
            filtered_df = self.df[mask]

            if filtered_df.empty:
                filter_desc = f"date range {start_date} to {end_date}"
                if passenger_counts and len(passenger_counts) > 0:
                    filter_desc += f" and passenger counts {passenger_counts}"
                
                self.logger.warning(f"No data found for the specified {filter_desc}")
                return {
                    "error": f"No data found for the specified {filter_desc}"
                }

            # Group by date and count trips
            daily_trips = filtered_df.groupby(
                filtered_df['tpep_pickup_datetime'].dt.date
            ).agg({
                'passenger_count': 'sum',
                'trip_distance': 'mean',
                'total_amount': 'sum'
            }).reset_index()

            # Calculate summary statistics
            summary_stats = {
                "total_trips": len(filtered_df),
                "total_passengers": int(filtered_df['passenger_count'].sum()),
                "average_daily_trips": float(len(filtered_df) / len(daily_trips)),
                "average_trip_distance": float(filtered_df['trip_distance'].mean()),
                "total_revenue": float(filtered_df['total_amount'].sum()),
                "average_daily_revenue": float(daily_trips['total_amount'].mean()),
                "max_trips_day": daily_trips['tpep_pickup_datetime'].max().strftime('%Y-%m-%d'),
                "min_trips_day": daily_trips['tpep_pickup_datetime'].min().strftime('%Y-%m-%d')
            }

            # Prepare response with enhanced data points
            response = {
                "data_points": {
                    "dates": daily_trips['tpep_pickup_datetime'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist(),
                    "trip_counts": [int(x) for x in daily_trips.index],
                    "passenger_counts": [int(x) for x in daily_trips['passenger_count']],
                    "average_distances": [float(x) for x in daily_trips['trip_distance']],
                    "daily_revenue": [float(x) for x in daily_trips['total_amount']]
                },
                "summary_statistics": summary_stats,
                "filter_info": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "passenger_counts": passenger_counts if passenger_counts else "all",
                    "total_days": len(daily_trips)
                }
            }

            return response

        except Exception as e:
            self.logger.error(f"Error in analyze_timeseries: {str(e)}")
            return None
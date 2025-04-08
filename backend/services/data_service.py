import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
import os

# Abstract Base Class for Analyses
class BaseAnalysis(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def analyze(self, df: pd.DataFrame, **kwargs):
        """
        Perform analysis on the provided DataFrame.

        Args:
            df: The pandas DataFrame to analyze.
            **kwargs: Analysis-specific parameters.

        Returns:
            A dictionary containing the analysis results or an error.
        """
        pass

# Concrete Implementation for Time Series Analysis
class TimeSeriesAnalysis(BaseAnalysis):
    def analyze(self, df: pd.DataFrame, start_date: str, end_date: str, passenger_counts: list = None, min_distance: float = None, max_distance: float = None):
        """
        Analyze trip data within the specified date range, passenger counts, and distance range and return time series data
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            passenger_counts: Optional list of passenger count values to filter by
            min_distance: Optional minimum trip distance (miles) to filter by
            max_distance: Optional maximum trip distance (miles) to filter by

        Returns:
            A dictionary containing the time series analysis results or an error message.
        """
        try:
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
            data_start = df['tpep_pickup_datetime'].min()
            data_end = df['tpep_pickup_datetime'].max()

            if start_dt > end_dt:
                return {
                    "error": "Start date must be before end date"
                }

            if end_dt < data_start or start_dt > data_end:
                return {
                    "error": f"Date range must be between {data_start.strftime('%Y-%m-%d')} and {data_end.strftime('%Y-%m-%d')}"
                }


            # Filter data by date range
            mask = (df['tpep_pickup_datetime'] >= start_dt) & (df['tpep_pickup_datetime'] <= end_dt)

            # Apply passenger count filter if provided
            if passenger_counts and len(passenger_counts) > 0:
                self.logger.info(f"Filtering by passenger counts: {passenger_counts}")
                mask = mask & (df['passenger_count'].isin(passenger_counts))

            # Apply distance filters if provided
            if min_distance is not None:
                self.logger.info(f"Filtering by minimum distance: {min_distance} miles")
                mask = mask & (df['trip_distance'] >= min_distance)

            if max_distance is not None:
                self.logger.info(f"Filtering by maximum distance: {max_distance} miles")
                mask = mask & (df['trip_distance'] <= max_distance)

            filtered_df = df[mask]

            if filtered_df.empty:
                filter_desc = f"date range {start_date} to {end_date}"
                if passenger_counts and len(passenger_counts) > 0:
                    filter_desc += f" and passenger counts {passenger_counts}"
                if min_distance is not None or max_distance is not None:
                    distance_desc = " and distance range "
                    if min_distance is not None:
                        distance_desc += f"from {min_distance} miles"
                    if min_distance is not None and max_distance is not None:
                        distance_desc += " to "
                    if max_distance is not None:
                        distance_desc += f"to {max_distance} miles"
                    filter_desc += distance_desc
                
                self.logger.warning(f"No data found for the specified {filter_desc}")
                return {
                    "error": f"No data found for the specified {filter_desc}"
                }

            # Group by date and aggregate
            daily_agg = filtered_df.groupby(
                filtered_df['tpep_pickup_datetime'].dt.date
            ).agg(
                trip_count=('tpep_pickup_datetime', 'size'), 
                total_passenger_count=('passenger_count', 'sum'),
                average_trip_distance=('trip_distance', 'mean'),
                total_daily_revenue=('total_amount', 'sum')
            ).reset_index()

            # Rename the date column for clarity
            daily_agg.rename(columns={'tpep_pickup_datetime': 'date'}, inplace=True)

            # Calculate overall summary statistics from the filtered data
            summary_stats = {
                "total_trips": int(filtered_df.shape[0]),
                "total_passengers": int(filtered_df['passenger_count'].sum()),
                "average_trip_distance": float(filtered_df['trip_distance'].mean()) if not filtered_df.empty else 0.0,
                "total_revenue": float(filtered_df['total_amount'].sum()),
                "average_daily_trips": float(daily_agg['trip_count'].mean()) if not daily_agg.empty else 0.0,
                "average_daily_revenue": float(daily_agg['total_daily_revenue'].mean()) if not daily_agg.empty else 0.0,
                "date_min_trips": daily_agg.loc[daily_agg['trip_count'].idxmin()]['date'].strftime('%Y-%m-%d') if not daily_agg.empty else "N/A",
                "date_max_trips": daily_agg.loc[daily_agg['trip_count'].idxmax()]['date'].strftime('%Y-%m-%d') if not daily_agg.empty else "N/A"
            }

            # Prepare response with enhanced data points
            response = {
                "data_points": {
                    "dates": daily_agg['date'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist(),
                    "trip_counts": daily_agg['trip_count'].astype(int).tolist(),
                    "passenger_counts": daily_agg['total_passenger_count'].astype(int).tolist(), # This is total daily passengers
                    "average_distances": daily_agg['average_trip_distance'].astype(float).round(2).tolist(), # This is avg daily distance
                    "daily_revenue": daily_agg['total_daily_revenue'].astype(float).round(2).tolist()
                },
                "summary_statistics": summary_stats,
                "filter_info": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "passenger_counts": passenger_counts if passenger_counts else "all",
                    "min_distance": min_distance,
                    "max_distance": max_distance,
                    "total_days_analyzed": int(len(daily_agg))
                }
            }

            return response

        except Exception as e:
            self.logger.exception(f"Error during time series analysis: {str(e)}") # Use logger.exception for stack trace
            return {
                "error": f"An internal error occurred during analysis: {str(e)}"
            }

# Data Service manages data loading and delegates analysis
class DataService:
    def __init__(self):
        self.df = None 
        self.data_path = Path(os.getenv("TAXI_DATA_PATH", "/Taxi_App/data/yellow_tripdata_2025-01_cleaned_optimized.parquet"))
        self.logger = logging.getLogger(__name__)

    def load_data(self):
        """Loads data from the parquet file if not already loaded."""
        if self.df is not None:
            self.logger.info("Data already loaded.")
            return True
        try:
            if not self.data_path.exists():
                self.logger.error(f"Data file not found at {self.data_path}")
                return False

            self.logger.info(f"Loading data from {self.data_path}")
            self.df = pd.read_parquet(self.data_path)

            # Validate expected columns and types
            expected_columns = {
                'tpep_pickup_datetime': 'datetime64[ns]', 
                'passenger_count': 'int64',
                'trip_distance': 'float64', 
                'total_amount': 'float64' 
            }

            missing_cols = [col for col in expected_columns if col not in self.df.columns]
            if missing_cols:
                 self.logger.error(f"Required columns not found in data: {', '.join(missing_cols)}")
                 self.df = None 
                 return False

            type_mismatches = {}
            for col, expected_dtype_str in expected_columns.items():
                 actual_dtype_str = str(self.df[col].dtype)
                 if expected_dtype_str.startswith('datetime64') and actual_dtype_str.startswith('datetime64'):
                     continue 
                 if expected_dtype_str.startswith('int') and actual_dtype_str.startswith('int'):
                     continue 
                 if expected_dtype_str.startswith('float') and actual_dtype_str.startswith('float'):
                      continue
                 if expected_dtype_str != actual_dtype_str:
                      type_mismatches[col] = {'actual': actual_dtype_str, 'expected': expected_dtype_str}

            if type_mismatches:
                 mismatch_details = "; ".join([f"{col} (is {d['actual']}, expected {d['expected']})" for col, d in type_mismatches.items()])
                 self.logger.warning(f"Column data type mismatches detected: {mismatch_details}")



            if self.df.empty:
                self.logger.error("Loaded data is empty")
                self.df = None 
                return False

            # Convert pickup datetime to correct type if needed and remove timezone
            if not pd.api.types.is_datetime64_any_dtype(self.df['tpep_pickup_datetime']):
                self.df['tpep_pickup_datetime'] = pd.to_datetime(self.df['tpep_pickup_datetime'])
            if self.df['tpep_pickup_datetime'].dt.tz is not None:
                self.logger.info("Removing timezone information from pickup datetime")
                self.df['tpep_pickup_datetime'] = self.df['tpep_pickup_datetime'].dt.tz_localize(None)


            if str(self.df['passenger_count'].dtype).startswith('Int'): 
                self.df['passenger_count'] = self.df['passenger_count'].astype(pd.Int64Dtype()).fillna(0).astype(int)
            else:
                 self.df['passenger_count'] = pd.to_numeric(self.df['passenger_count'], errors='coerce').fillna(0).astype(int)

            if str(self.df['trip_distance'].dtype).startswith('Float'): 
                 self.df['trip_distance'] = self.df['trip_distance'].astype(pd.Float64Dtype()).fillna(0.0).astype(float)
            else:
                 self.df['trip_distance'] = pd.to_numeric(self.df['trip_distance'], errors='coerce').fillna(0.0).astype(float)

            if str(self.df['total_amount'].dtype).startswith('Float'): 
                 self.df['total_amount'] = self.df['total_amount'].astype(pd.Float64Dtype()).fillna(0.0).astype(float)
            else:
                 self.df['total_amount'] = pd.to_numeric(self.df['total_amount'], errors='coerce').fillna(0.0).astype(float)


            self.logger.info(f"Successfully loaded and validated data with {len(self.df)} records")
            return True

        except Exception as e:
            self.logger.exception(f"Error loading or validating data: {str(e)}") 
            self.df = None 
            return False

    def perform_analysis(self, analysis: BaseAnalysis, **kwargs):
        """
        Performs the given analysis on the loaded data.

        Args:
            analysis: An instance of a class inheriting from BaseAnalysis.
            **kwargs: Parameters required by the specific analysis's 'analyze' method.

        Returns:
            The result from the analysis object's 'analyze' method, or None if data loading fails.
        """
        if self.df is None:
            self.logger.info("Data not loaded. Attempting to load data first.")
            if not self.load_data():
                self.logger.error("Failed to load data. Cannot perform analysis.")
                # Return an error structure consistent with analysis results
                return {"error": "Failed to load necessary data for analysis."}

        self.logger.info(f"Performing analysis using {type(analysis).__name__}")
        try:
             # Pass the DataFrame and other arguments to the analysis object
             return analysis.analyze(self.df, **kwargs)
        except Exception as e:
             self.logger.exception(f"An unexpected error occurred while delegating to {type(analysis).__name__}: {str(e)}")
             return {"error": "An unexpected error occurred during the analysis process."}



    def analyze_timeseries(self, start_date, end_date, passenger_counts=None, min_distance=None, max_distance=None):
        """
        Specific method to trigger Time Series Analysis.
        """
        self.logger.info("Initiating time series analysis.")
        time_series_analyzer = TimeSeriesAnalysis(self.logger)

        analysis_args = {
            "start_date": start_date,
            "end_date": end_date,
            "passenger_counts": passenger_counts,
            "min_distance": min_distance,
            "max_distance": max_distance
        }

        return self.perform_analysis(time_series_analyzer, **analysis_args)
# Taxi Data Dashboard - User Guide

## 1. Introduction & Purpose

Welcome! This is an interactive dashboard designed for exploring and analyzing New York City (NYC) Yellow Taxi trip data.

**What is this app?**
This full-stack web application provides an easy-to-use interface to query a specific subset of the vast NYC taxi dataset. It uses a Flask backend for data handling and a Streamlit frontend for the user interface and visualizations.

**Who is it for?**
It's built for city officials, urban planners, academic researchers, transportation analysts, and anyone interested in understanding urban mobility patterns within NYC.

**What can you do with it?**
You can apply filters based on:
*   Pickup Date Range
*   Trip Distance (Mileage)
*   Number of Passengers

The dashboard will then dynamically update to show visualizations and statistics based on the trips that match your criteria.

**Goal:**
The primary goal is to make insights from this rich dataset more accessible, reducing the technical barriers often associated with analyzing large datasets. It aims to help users identify trends, understand service usage, and potentially inform data-driven decisions related to urban transportation.

## 2. Data Source & Context

The data powering this dashboard originates from the official **NYC Taxi & Limousine Commission (TLC)**. This data is publicly available and provides a valuable resource for understanding taxi operations in the city.

*   **Source:** You can find the original datasets on the [NYC TLC Trip Record Data page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
*   **Dataset Used:** This dashboard currently utilizes the **Yellow Taxi Trip Records**.
*   **Time Period:** To ensure responsiveness and manage data volume, this application currently **only includes data for January 2025**. Findings reflect patterns within this specific month.

*(Note: No detailed data dictionary is included here, as the focus is on the filters provided in the dashboard.)*

## 3. Data Preparation & Cleaning

Raw public data often contains inconsistencies or requires cleaning for meaningful analysis. Before loading the data into this application, the following key preparation steps were performed on the January 2025 Yellow Taxi dataset:

*   **Handling Missing Values:** Records with `None` (missing) values in critical fields used by the filters were removed.
*   **Trip Distance Validation:**
    *   Ensured `trip_distance` was greater than 0 miles (trips logged with zero distance or negative distance were excluded).
    *   Removed trips with `trip_distance` greater than 100 miles, as these are often considered outliers or potential data errors for typical yellow taxi usage within the city context.
*   **Fare Amount Validation:**
    *   Ensured the `total_amount` was greater than $0.
    *   Removed trips where the `total_amount` exceeded $2,000, treating these as likely data errors.
*   **Passenger Count Validation:**
    *   Ensured `passenger_count` was greater than 0.
*   **Performance Optimization:** Columns from the original dataset that are not directly used for filtering or visualization within *this specific dashboard* were removed. This significantly speeds up data processing and improves the application's responsiveness.

These steps aim to provide a cleaner, more reliable dataset focused on typical taxi trip patterns for analysis within this tool.

## 4. How to Use the Dashboard

The application interface is designed for ease of use:

**Layout:**
*   **Sidebar (Left):** This panel contains all the available **Filters** and the **Apply Filters** button.
*   **Main Panel (Right):** This area displays the **Results** based on your filter selections. This includes summary statistics, charts/visualizations, and an option to download the report.

**Filtering Panel (Sidebar):**
1.  **Date Range Selector:** Use the calendar selection to define the start and end pickup dates for the trips you want to analyze within January 2025.
2.  **Mileage Range Selector:** Adjust the two sliders along with input boxes to set the minimum and maximum `trip_distance` (in miles) for the trips to include.
3.  **Passenger Count Selector:** Select the minimum and maximum number of passengers (`passenger_count`) per trip using the checkboxes.
4.  **Apply Filters Button:** After setting your desired filters, **you MUST click the 'Apply Filters' button**. The dashboard will then query the backend and update the results in the main panel. 

**Results Display (Main Panel):**
*   After clicking 'Apply Filters', this area will update to show:
    *   Key metrics 
    *   Visualizations 

## 5. Understanding the Filters (Why Use Them?)

The filters provided allow you to segment the data in meaningful ways:

*   **Date Range:** Essential for temporal analysis. Allows you to isolate specific periods like:
    *   Weekdays vs. Weekends: Compare demand and trip characteristics.
    *   Specific Weeks: Observe trends across the month (e.g., comparing the first week of Jan to the last).
    *   (If broader data were included, you could analyze holidays or seasons).
*   **Mileage Range:** Crucial for understanding trip types and economics.
    *   Short Trips (e.g., 0-3 miles): Analyze local travel patterns, potentially within boroughs.
    *   Medium Trips (e.g., 3-10 miles): Explore common commutes or cross-neighborhood travel.
    *   Long Trips (e.g., 10+ miles): Identify potential airport runs or longer inter-borough travel, analyze their frequency and fare characteristics.
*   **Passenger Count:** Helps analyze how taxis are utilized for group or individual travel.
    *   Single Passenger Trips: Understand the dominant mode of individual travel.
    *   Multi-Passenger Trips (e.g., 2+ or 3+): Analyze shared rides, family or group travel patterns. 

## 6. Example Use Cases

Here are a couple of ways you might combine filters to explore the data:

*   **Example 1: Analyzing Long Weekend Trips**
    *   Set the **Date Range** to cover a specific Friday-to-Sunday period within January 2025.
    *   Set the **Mileage Range** sliders to a minimum of `10` miles and a maximum of `100` miles.
    *   Check all **Passenger Count**
    *   Click **'Apply Filters'**.
    *   This helps understand the volume and nature of longer-distance travel during weekends.

*   **Example 2: Exploring Short, Multi-Passenger Rides during Peak Hours (Hypothetical)**
    *   Set the **Date Range** to include weekdays (e.g., a Monday-Friday period). (Note: Time-of-day filtering isn't implemented here, but is a common next step).
    *   Set the **Mileage Range** sliders to a minimum of `0` miles and a maximum of `3` miles.
    *   Set the **Passenger Count** sliders to a minimum of `3` passengers and a maximum of (e.g.) `6`.
    *   Click **'Apply Filters'**.
    *   *Observe:* This helps identify patterns for short group trips, which might be common for families, friends sharing rides locally, or potentially related to specific local events or commuting patterns.

## 7. Known Limitations

Please be aware of the following limitations when interpreting the results:

*   **Data Accuracy:** The analysis is based on the data provided by the NYC TLC. Any inaccuracies or biases present in the source data will be reflected in the results.
*   **Limited Time Scope:** This dashboard **only includes data for January 2025**. Findings are specific to this month and may not represent patterns from other times of the year or different years.
*   **Yellow Taxi Only:** Only Yellow Taxi data is included. Trends might differ for Green Taxis or For-Hire Vehicles (FHVs).
*   **No Location Analysis:** This version of the dashboard **does not include analysis based on pickup or dropoff locations** (e.g., boroughs or taxi zones). It focuses solely on the temporal, distance, and passenger count dimensions.
*   **Data Cleaning Impact:** The cleaning steps described in Section 3 intentionally remove certain records (e.g., outliers, missing data). While this improves focus, it means the analysis is performed on a subset of the original raw data.

---

We hope this guide helps you effectively use the Taxi Data Dashboard!
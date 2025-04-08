import streamlit as st
from pathlib import Path

st.title("Static Report: NYC Yellow Taxi Insights (January 2025)")

# Define the introduction content
intro_content = """
This report presents some pre-generated insights based on the cleaned **NYC Yellow Taxi dataset for January 2025**.
The data was sourced from the NYC TLC public data portal. These visualizations provide a static snapshot
of typical patterns observed during that month.
"""

# Define the path to the assets relative to this script file
IMAGE_DIR = Path("assets/")

# Display intro
st.markdown(intro_content)

st.divider()

# --- Insight 1: Daily Trip Volume ---
st.subheader("Daily Trip Volume Trends")
col1, col2 = st.columns([1, 2]) # Ratio for text and image size

insight1_content = """
This chart shows the total number of Yellow Taxi trips recorded each day in January 2025.

**Observations:**
*   There's a clear weekly pattern, with **lower trip volumes typically seen on weekends** (Saturdays and Sundays) compared to weekdays.
*   Mid-week days (Tuesday-Thursday) often show the highest activity.
*   There might be slight variations possibly due to weather or specific events, but the overall weekly cycle is dominant.
"""

with col1:
    st.markdown(insight1_content)

with col2:
    image_path = IMAGE_DIR / "trips_per_day.png"
    if image_path.is_file():
        st.image(str(image_path), caption="Number of Yellow Taxi trips per day in January 2025.")
    else:
        st.warning(f"Image not found: {image_path}")

st.divider()

# --- Insight 2: Trip Distance Distribution ---
st.subheader("How Far Do Taxis Go?")
col1, col2 = st.columns([2, 1]) # Image first this time

insight2_content = """
This histogram illustrates the frequency of different trip distances.

**Observations:**
*   The vast majority of trips are **relatively short**, often under 5 miles.
*   There's a sharp drop-off in frequency as distance increases.
*   This highlights the primary role of yellow taxis for shorter, within-borough or nearby-borough travel, though longer trips (like airport runs) do occur.
*   *(Note: Trips > 100 miles were excluded during cleaning).*
"""

with col1:
    image_path = IMAGE_DIR / "distance_histogram.png"
    if image_path.is_file():
        st.image(str(image_path), caption="Distribution of trip distances (miles) for Jan 2025.")
    else:
        st.warning(f"Image not found: {image_path}")

with col2:
    st.markdown(insight2_content)


st.divider()

# --- Insight 3: Passenger Counts ---
st.subheader("Typical Number of Passengers")
col1, col2 = st.columns([1, 2])

insight3_content = """
This bar chart shows how many trips were taken with a specific number of passengers.

**Observations:**
*   The most common scenario by far is a **single passenger**.
*   Two-passenger trips are the next most frequent.
*   Trips with 3, 4, 5, or 6+ passengers are progressively less common.
*   This reflects typical taxi usage patterns, often involving individuals or pairs.
*   *(Note: Trips with 0 passengers were excluded during cleaning).*
"""

with col1:
    st.markdown(insight3_content)

with col2:
    image_path = IMAGE_DIR / "passenger_count_distribution.png"
    if image_path.is_file():
        st.image(str(image_path), caption="Frequency of passenger counts per trip for Jan 2025.")
    else:
        st.warning(f"Image not found: {image_path}")


st.divider()

# --- Insight 4: Fare Distribution ---
st.subheader("Distribution of Trip Fares")
col1, col2 = st.columns([2, 1])

insight4_content = """
This histogram shows the distribution of the `total_amount` paid per trip (includes fare, tolls, tips, etc.).

**Observations:**
*   Similar to distance, most fares fall into the lower range, typically under $20-$30.
*   The distribution is right-skewed, meaning while most fares are low, there's a long tail of higher-cost trips.
*   This aligns with the prevalence of shorter trips observed earlier.
*   *(Note: Trips > $2000 total amount were excluded during cleaning).*
"""

with col1:
     image_path = IMAGE_DIR / "fare_amount_histogram.png"
     if image_path.is_file():
        st.image(str(image_path), caption="Distribution of total fare amounts ($) for Jan 2025.")
     else:
        st.warning(f"Image not found: {image_path}")

with col2:
    st.markdown(insight4_content)

st.divider()

footer_content = """
*This static report provides a basic overview. The interactive dashboard allows for more dynamic exploration by applying filters.*
"""
st.markdown(footer_content)
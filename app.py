import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("nasa_neo.db")
cursor = conn.cursor()

st.set_page_config(page_title="NASA Near-Earth Object (NEO) Tracking & Insights", layout="wide")
st.title("🚀 NASA Asteroid Tracker")

st.sidebar.title("Asteroid Approaches")
section = st.sidebar.radio("Choose View:", ["Filter Criteria", "Queries"])

if section == "Filter Criteria":
    st.subheader("🔍 Filtered Asteroid Data")

    mag_min, mag_max = st.slider("Min Magnitude", 13.0, 35.0, (13.0, 25.0))
    dia_min, dia_max = st.slider("Estimated Diameter (km)", 0.0, 20.0, (0.0, 5.0))
    vel_min, vel_max = st.slider("Relative Velocity (km/h)", 0.0, 180000.0, (0.0, 50000.0))
    au = st.slider("Astronomical Unit (AU)", 0.0, 1.0, 0.3)
    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2025-04-13"))
    hazard = st.selectbox("Only Show Potentially Hazardous", ["All", "Yes", "No"])

    query = f"""
        SELECT a.*, ca.close_approach_date, ca.relative_velocity_kmph, ca.astronomical
        FROM asteroids a
        JOIN close_approach ca ON a.id = ca.neo_reference_id
        WHERE a.absolute_magnitude_h BETWEEN {mag_min} AND {mag_max}
        AND a.estimated_diameter_min_km >= {dia_min}
        AND a.estimated_diameter_max_km <= {dia_max}
        AND ca.relative_velocity_kmph BETWEEN {vel_min} AND {vel_max}
        AND ca.astronomical <= {au}
        AND ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
    """

    if hazard == "Yes":
        query += " AND a.is_potentially_hazardous_asteroid = 1"
    elif hazard == "No":
        query += " AND a.is_potentially_hazardous_asteroid = 0"

    filtered_data = pd.read_sql_query(query, conn)
    st.dataframe(filtered_data)

elif section == "Queries":
    st.subheader("🛰️ Asteroid Data Insights ")

    query_options = {
        "1. Asteroid Approach Count":
            """SELECT name, COUNT(*) AS approach_count
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               GROUP BY name
               ORDER BY approach_count DESC""",

        "2. Average Velocity per Asteroid":
            """SELECT name, AVG(relative_velocity_kmph) AS avg_velocity
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               GROUP BY name
               ORDER BY avg_velocity DESC""",

        "3. Top 10 Fastest Asteroids":
            """SELECT name, MAX(relative_velocity_kmph) AS max_velocity
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               GROUP BY name
               ORDER BY max_velocity DESC LIMIT 10""",

        "4. Hazardous Asteroids with >3 Approaches":
            """SELECT name, COUNT(*) AS times
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE is_potentially_hazardous_asteroid = 1
               GROUP BY name
               HAVING times > 3""",

        "5. Month with Most Approaches":
            """SELECT strftime('%Y-%m', close_approach_date) AS month, COUNT(*) AS count
               FROM close_approach
               GROUP BY month
               ORDER BY count DESC LIMIT 1""",

        "6. Fastest Ever Asteroid":
            """SELECT name, MAX(relative_velocity_kmph) AS max_velocity
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id""",

        "7. Largest Asteroids by Diameter":
            """SELECT name, estimated_diameter_max_km
               FROM asteroids
               ORDER BY estimated_diameter_max_km DESC""",

        "8. Asteroids Approaching Closer Over Time":
            """SELECT name, close_approach_date, miss_distance_km
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               ORDER BY close_approach_date, miss_distance_km""",

        "9. Closest Approaches (Name + Date + Distance)":
            """SELECT name, close_approach_date, miss_distance_km
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               ORDER BY miss_distance_km ASC""",

        "10. Asteroids > 50,000 km/h":
            """SELECT DISTINCT name, relative_velocity_kmph
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE relative_velocity_kmph > 50000
               ORDER BY relative_velocity_kmph DESC""",

        "11. Count of Approaches Per Month":
            """SELECT strftime('%Y-%m', close_approach_date) AS month, COUNT(*) AS total
               FROM close_approach
               GROUP BY month
               ORDER BY month""",

        "12. Brightest Asteroid (Lowest Magnitude)":
            """SELECT name, MIN(absolute_magnitude_h) AS brightness
               FROM asteroids""",

        "13. Hazardous vs Non-Hazardous Count":
            """SELECT is_potentially_hazardous_asteroid AS hazardous, COUNT(*) AS total
               FROM asteroids
               GROUP BY hazardous""",

        "14. Passed Closer Than Moon (< 1 LD)":
            """SELECT name, close_approach_date, miss_distance_lunar
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE miss_distance_lunar < 1
               ORDER BY miss_distance_lunar""",

        "15. Within 0.05 AU":
            """SELECT name, close_approach_date, astronomical
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE astronomical < 0.05
               ORDER BY astronomical""",

        "16. Asteroids with Wide Diameter Range (> 2 km)":
            """SELECT name, estimated_diameter_min_km, estimated_diameter_max_km,
                      (estimated_diameter_max_km - estimated_diameter_min_km) AS diameter_variance
               FROM asteroids
               WHERE (estimated_diameter_max_km - estimated_diameter_min_km) > 2
               ORDER BY diameter_variance DESC""",

        "17. Average Velocity by Orbiting Body":
            """SELECT orbiting_body, AVG(relative_velocity_kmph) AS avg_velocity
               FROM close_approach
               GROUP BY orbiting_body
               ORDER BY avg_velocity DESC""",

        "18. Unique Asteroids That Approached Earth":
            """SELECT COUNT(DISTINCT a.id) AS unique_asteroid_count
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE orbiting_body = 'Earth'""",

        "19. Top 10 Closest Approaches by Lunar Distance":
            """SELECT name, close_approach_date, miss_distance_lunar
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               ORDER BY miss_distance_lunar ASC
               LIMIT 10""",

        "20. Most Frequently Approaching Hazardous Asteroid":
            """SELECT name, COUNT(*) AS approach_count
               FROM asteroids a
               JOIN close_approach ca ON a.id = ca.neo_reference_id
               WHERE is_potentially_hazardous_asteroid = 1
               GROUP BY name
               ORDER BY approach_count DESC
               LIMIT 1""",
    
    }

    selected_query = st.selectbox("Choose a SQL Insight", list(query_options.keys()))
    result = pd.read_sql_query(query_options[selected_query], conn)
    st.dataframe(result)

conn.close()
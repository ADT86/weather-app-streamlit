import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import numpy as np

# List of cities with coordinates
cities = [
    {"name": "Oslo", "lat": 59.91, "lon": 10.75},
    {"name": "Kristiansand", "lat": 58.15, "lon": 8.00},
    {"name": "Haugesund", "lat": 59.41, "lon": 5.27},
    {"name": "Stavanger", "lat": 58.97, "lon": 5.73},
    {"name": "Klepp", "lat": 58.77, "lon": 5.63},
    {"name": "Tromso", "lat": 69.65, "lon": 18.96},
    {"name": "Bergen", "lat": 60.39, "lon": 5.32},
    {"name": "Hamar", "lat": 60.79, "lon": 11.06},
    {"name": "Kristiansund", "lat": 63.11, "lon": 7.73},
    {"name": "Skien og porsgrunn", "lat": 59.21, "lon": 9.61},
    {"name": "Baerum", "lat": 59.91, "lon": 10.52},
    {"name": "Lillehammer", "lat": 61.12, "lon": 10.47},
    {"name": "Gjovik", "lat": 60.80, "lon": 10.69},
    {"name": "Bodo", "lat": 67.28, "lon": 14.37},
    {"name": "Moss", "lat": 59.44, "lon": 10.66},
    {"name": "Halden", "lat": 59.12, "lon": 11.39},
    {"name": "Molde", "lat": 62.74, "lon": 7.16},
    {"name": "Nesttun", "lat": 60.32, "lon": 5.36},
    {"name": "Harstad", "lat": 68.80, "lon": 16.54},
    {"name": "Kongsberg", "lat": 59.67, "lon": 9.65},
    {"name": "Sandnes", "lat": 58.85, "lon": 5.73},
    {"name": "Elverum", "lat": 60.88, "lon": 11.56},
    {"name": "Larvik", "lat": 59.05, "lon": 10.03},
    {"name": "Sarpsborg", "lat": 59.28, "lon": 11.11},
    {"name": "Honefoss", "lat": 60.17, "lon": 10.26},
    {"name": "Horten", "lat": 59.42, "lon": 10.48},
    {"name": "Ålesund", "lat": 62.47, "lon": 6.15},
    {"name": "Lillestrom", "lat": 59.95, "lon": 11.05},
    {"name": "Sandefjord", "lat": 59.13, "lon": 10.22},
    {"name": "Drammen", "lat": 59.75, "lon": 10.20},
    {"name": "Asane", "lat": 60.48, "lon": 5.32},
    {"name": "Ski", "lat": 59.72, "lon": 10.83},
    {"name": "Stord", "lat": 59.78, "lon": 5.50},
    {"name": "Trondheim", "lat": 63.43, "lon": 10.40},
    {"name": "Fredrikstad", "lat": 59.22, "lon": 10.93},
    {"name": "Jessheim", "lat": 60.14, "lon": 11.18},
    {"name": "Arendal", "lat": 58.46, "lon": 8.77},
    {"name": "Tonsberg", "lat": 59.27, "lon": 10.41},
    {"name": "Fyllingsdalen", "lat": 60.35, "lon": 5.31},
    {"name": "Heimdal", "lat": 63.34, "lon": 10.35},
    {"name": "Grimstad", "lat": 58.34, "lon": 8.59}
]

# Streamlit app
st.title("🌦️ Weather in Norwegian Cities")

# Function to get weather data for a city
def get_weather_data(lat, lon):
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {"User-Agent": "MyWeatherApp/1.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Function to extract today's temperature timeline
def get_today_temperature_timeline(weather_data):
    today = date.today().isoformat()
    temps = []
    times = []
    
    for entry in weather_data["properties"]["timeseries"]:
        entry_date = entry["time"].split("T")[0]
        if entry_date == today:
            times.append(datetime.fromisoformat(entry["time"].replace("Z", "+00:00")))
            temps.append(entry["data"]["instant"]["details"]["air_temperature"])
    
    return pd.DataFrame({"Time": times, "Temperature": temps})

# Function to calculate daily precipitation for a city
def get_daily_precipitation(weather_data):
    today = date.today().isoformat()
    precipitation_amounts = []
    
    for entry in weather_data["properties"]["timeseries"]:
        entry_date = entry["time"].split("T")[0]
        if entry_date == today and "next_1_hours" in entry["data"]:
            if "details" in entry["data"]["next_1_hours"]:
                precip = entry["data"]["next_1_hours"]["details"].get("precipitation_amount", 0)
                precipitation_amounts.append(precip)
    
    return sum(precipitation_amounts) if precipitation_amounts else 0

# Calculate precipitation data once for all cities (cached)
@st.cache_data
def get_all_cities_precipitation():
    precipitation_data = []
    for city in cities:
        weather_data = get_weather_data(city["lat"], city["lon"])
        if weather_data:
            daily_precip = get_daily_precipitation(weather_data)
            precipitation_data.append({
                "City": city["name"],
                "Expected Precipitation (mm)": round(daily_precip, 2)
            })
    return precipitation_data

city_names = [city["name"] for city in cities]
selected_city_name = st.selectbox("Choose a city", city_names)

if selected_city_name:
    city_info = next(c for c in cities if c["name"] == selected_city_name)
    lat, lon = city_info["lat"], city_info["lon"]
    
    weather_data = get_weather_data(lat, lon)

    if weather_data:
        now = weather_data["properties"]["timeseries"][0]
        time = now["time"]
        details = now["data"]["instant"]["details"]

        # Current weather section
        st.subheader(f"🌤️ Current Weather in {selected_city_name}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌡️ Temperature (°C)", details["air_temperature"])
            st.metric("💨 Wind Speed (m/s)", details.get("wind_speed", "N/A"))
        
        with col2:
            st.metric("💧 Humidity (%)", details.get("relative_humidity", "N/A"))
            st.metric("☁️ Cloud Cover (%)", details.get("cloud_area_fraction", "N/A"))
        
        with col3:
            st.metric("🧭 Wind Direction (°)", details.get("wind_from_direction", "N/A"))
        
        st.caption(f"Last updated: {time}")
        
        # Temperature timeline chart
        st.subheader(f"📈 Today's Temperature Timeline - {selected_city_name}")
        temp_df = get_today_temperature_timeline(weather_data)
        
        if not temp_df.empty:
            fig = px.line(temp_df, x="Time", y="Temperature", 
                         title=f"Temperature Throughout the Day - {selected_city_name}",
                         labels={"Temperature": "Temperature (°C)", "Time": "Time"})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No temperature timeline data available for today.")
            
    else:
        st.error("Could not fetch weather data. Try again later.")

# Top 3 cities with highest precipitation
st.subheader("🌧️ Top 3 Cities with Highest Expected Precipitation Today")

with st.spinner("Loading precipitation data for all cities..."):
    precipitation_data = get_all_cities_precipitation()
    
    if precipitation_data:
        precip_df = pd.DataFrame(precipitation_data)
        precip_df = precip_df.sort_values("Expected Precipitation (mm)", ascending=False)
        top_3 = precip_df.head(3)
        
        if top_3["Expected Precipitation (mm)"].sum() > 0:
            for i, (_, row) in enumerate(top_3.iterrows(), 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{i}. {row['City']}**")
                with col2:
                    st.metric("", f"{row['Expected Precipitation (mm)']} mm")
        else:
            st.info("No significant precipitation expected in any Norwegian cities today! ☀️")
    else:
        st.error("Could not fetch precipitation data for cities.")

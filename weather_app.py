import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Weather & Climate Analytics Dashboard", layout="wide")

st.title("🌤️ Weather & Climate Analytics Dashboard")
st.markdown("Enter a city name to get current weather conditions and a 7-day forecast.")

col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("City Name", placeholder="e.g. New York, London, Tokyo")
with col2:
    units = st.selectbox("Units", ["Fahrenheit", "Celsius"])

unit_param  = "imperial" if units == "Fahrenheit" else "metric"
unit_symbol = "°F"       if units == "Fahrenheit" else "°C"
wind_unit   = "mph"      if units == "Fahrenheit" else "m/s"

API_KEY = "78e5ad49bfd0591fe745812536a3f85c"

def get_weather(city_name, unit):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={unit}"
    return requests.get(url).json()

def get_forecast(city_name, unit):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={unit}&cnt=40"
    return requests.get(url).json()

if city:
    with st.spinner("Fetching weather data..."):
        weather_data  = get_weather(city, unit_param)
        forecast_data = get_forecast(city, unit_param)

    if weather_data.get("cod") != 200:
        st.error(f"City not found: {weather_data.get('message', 'Unknown error')}. Please check the city name.")
    else:
        st.subheader(f"📍 Current Conditions — {weather_data['name']}, {weather_data['sys']['country']}")

        temp        = weather_data["main"]["temp"]
        feels_like  = weather_data["main"]["feels_like"]
        humidity    = weather_data["main"]["humidity"]
        wind_speed  = weather_data["wind"]["speed"]
        description = weather_data["weather"][0]["description"].title()
        visibility  = weather_data.get("visibility", 0) / 1000

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature",  f"{temp:.1f}{unit_symbol}")
        c2.metric("Feels Like",   f"{feels_like:.1f}{unit_symbol}")
        c3.metric("Humidity",     f"{humidity}%")
        c4.metric("Wind Speed",   f"{wind_speed} {wind_unit}")

        st.info(f"**Condition:** {description}  |  **Visibility:** {visibility:.1f} km")

        st.subheader("📅 5-Day Forecast (every 3 hours)")

        if forecast_data.get("cod") == "200":
            import pandas as pd

            rows = []
            for item in forecast_data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                rows.append({
                    "Date/Time":    dt.strftime("%a %b %d %H:%M"),
                    f"Temp ({unit_symbol})": round(item["main"]["temp"], 1),
                    "Humidity (%)": item["main"]["humidity"],
                    "Condition":    item["weather"][0]["description"].title(),
                    f"Wind ({wind_unit})": item["wind"]["speed"],
                })

            df = pd.DataFrame(rows)

            st.line_chart(df.set_index("Date/Time")[[f"Temp ({unit_symbol})", "Humidity (%)"]],
                          use_container_width=True)

            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Forecast data unavailable.")

st.markdown("---")
st.caption("Data provided by OpenWeatherMap API. Built with Streamlit.")
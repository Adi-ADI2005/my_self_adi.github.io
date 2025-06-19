from flask import Flask, render_template, request
import requests #Fetch data from APIs, websites, and web services. and handel the HTTP request.
from datetime import datetime # used to check the current data and time

app = Flask(__name__)

API_KEY = "206457ab3cf06fd22c7c03a5e0648f79"  #  API key to get weather from open weather .
KELVIN = 273.15  

#use to convert utc timestamp to local time with day name.
def format_time_with_day(utc_timestamp, timezone_offset):
    """Convert UTC timestamp to local time with day name."""
    local_time = datetime.utcfromtimestamp(utc_timestamp + timezone_offset)
    return local_time.strftime("%A, %d-%m-%Y %H:%M") 

# featch the data of weather  in daily basic
def dw_home():
    weather_data = None
    hourly_data = None
    error_msg = None
    current_date = datetime.now().strftime("%d-%m-%Y")  

    if request.method == "POST":
        cityname = request.form.get("city", "").strip()

        if not cityname:
            error_msg = "Please enter a city name."
        else:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={cityname}&appid={API_KEY}" # url to call api

            try:
                response = requests.get(weather_url)
                response.raise_for_status()
                weather_info = response.json()

                if weather_info.get("cod") == 200:
                    timezone_offset = weather_info["timezone"]  
                    # Fetch day by day  weather forecast
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={cityname}&appid={API_KEY}"
                    forecast_response = requests.get(forecast_url)
                    forecast_data = forecast_response.json()

                    if "list" in forecast_data:
                        hourly_forecast = []
                        for forecast in forecast_data["list"][:8]:  
                            formatted_datetime = format_time_with_day(forecast["dt"], timezone_offset)
                            # show the weather data of current data . gape of 3hr
                            hourly_forecast.append({
                                "datetime": formatted_datetime, 
                                "temperature": int(forecast["main"]["temp"] - KELVIN),
                                "humidity": forecast["main"]["humidity"],
                                "pressure": forecast["main"]["pressure"],
                                "cloudiness": forecast["clouds"]["all"],
                                "description": forecast["weather"][0]["description"].capitalize()
                            })

                        hourly_data = hourly_forecast
                    else:
                        error_msg = "Hourly weather data is unavailable. Try again later."
                       # show the basic data of that location with weather condition
                    weather_data = {
                        "city": cityname.capitalize(),
                        "temperature": int(weather_info["main"]["temp"] - KELVIN),
                        "feels_like": int(weather_info["main"]["feels_like"] - KELVIN),
                        "max_temp": int(weather_info["main"]["temp_max"] - KELVIN),
                        "min_temp": int(weather_info["main"]["temp_min"] - KELVIN),
                        "pressure": weather_info["main"]["pressure"],
                        "humidity": weather_info["main"]["humidity"],
                        "cloudiness": weather_info["clouds"]["all"],
                        "description": weather_info["weather"][0]["description"].capitalize(),
                        "visibility": weather_info.get("visibility", "N/A"),
                        "sea_level": weather_info["main"].get("sea_level", "N/A"),
                        "grnd_level": weather_info["main"].get("grnd_level", "N/A"),
                        "sunrise": format_time_with_day(weather_info["sys"]["sunrise"], timezone_offset),
                        "sunset": format_time_with_day(weather_info["sys"]["sunset"], timezone_offset),
                    }
                else:
                    error_msg = f"Weather data for '{cityname}' not found! Please enter a valid city."

            except requests.exceptions.RequestException as e:
                error_msg = f"Error fetching weather data: {e}"

    return render_template("demo.html", date=current_date, weather=weather_data, hourly=hourly_data, error=error_msg)

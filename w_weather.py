from flask import Flask, render_template, request
import requests #Fetch data from APIs, websites, and web services. and handel the HTTP request.
from datetime import datetime # used to check the current data and time
from collections import defaultdict # helps manage missing keys automatically

app = Flask(__name__)

API_KEY = "206457ab3cf06fd22c7c03a5e0648f79"  #  API key to get weather from open weather .
KELVIN = 273.15  # Constant for Kelvin to Celsius conversion

#Convert UTC timestamp to local time using timezone offset.
def time_Format_For_Location(utc_timestamp, timezone_offset):
    """Convert UTC timestamp to local time using timezone offset."""
    local_time = datetime.utcfromtimestamp(utc_timestamp + timezone_offset)
    return local_time.strftime("%H:%M")

# featch the data of weather  in weeakly basic
@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    daily_data = None
    weekly_data = None
    error_msg = None
    current_date = datetime.now().strftime("%d-%m-%Y")  # Current date in DD-MM-YYYY format

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

                    # Fetch 5-day weather forecast
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={cityname}&appid={API_KEY}"
                    forecast_response = requests.get(forecast_url)
                    forecast_data = forecast_response.json()

                    if "list" in forecast_data:
                        daily_forecast = defaultdict(list)
                        weekly_summary = defaultdict(lambda: {"temp_max": -1000, "temp_min": 1000, "humidity": []})

                        for forecast in forecast_data["list"]:
                            forecast_time = datetime.utcfromtimestamp(forecast["dt"] + timezone_offset)
                            formatted_date = forecast_time.strftime("%d-%m-%Y")
                            formatted_time = forecast_time.strftime("%H:%M")
                            weekday = forecast_time.strftime("%A")  # Get day name

                            temp = int(forecast["main"]["temp"] - KELVIN)
                            humidity = forecast["main"]["humidity"]
                            pressure = forecast["main"]["pressure"]
                            cloudiness = forecast["clouds"]["all"]
                            description = forecast["weather"][0]["description"].capitalize()

                            # Group weather data by date
                            daily_forecast[formatted_date].append({
                                "time": formatted_time,
                                "temperature": temp,
                                "humidity": humidity,
                                "pressure": pressure,
                                "cloudiness": cloudiness,
                                "description": description
                            })

                            # Weekly summary logic
                            weekly_summary[weekday]["temp_max"] = max(weekly_summary[weekday]["temp_max"], temp)
                            weekly_summary[weekday]["temp_min"] = min(weekly_summary[weekday]["temp_min"], temp)
                            weekly_summary[weekday]["humidity"].append(humidity)

                        # Convert weekly data into a presentable format
                        weekly_data = []
                        for day, values in weekly_summary.items():
                            weekly_data.append({
                                "day": day,
                                "max_temp": values["temp_max"],
                                "min_temp": values["temp_min"],
                                "avg_humidity": sum(values["humidity"]) // len(values["humidity"])
                            })

                        daily_data = dict(daily_forecast)
                    else:
                        error_msg = "Daily & Weekly weather data is unavailable. Try again later."
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
                        "sunrise": time_Format_For_Location(weather_info["sys"]["sunrise"], timezone_offset),
                        "sunset": time_Format_For_Location(weather_info["sys"]["sunset"], timezone_offset),
                    }
                else:
                    error_msg = f"Weather data for '{cityname}' not found! Please enter a valid city."

            except requests.exceptions.RequestException as e:
                error_msg = f"Error fetching weather data: {e}"

    return render_template("demo.html", date=current_date, weather=weather_data, daily=daily_data, weekly=weekly_data, error=error_msg)

if __name__ == "__main__":
    app.run(debug=True)

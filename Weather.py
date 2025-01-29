import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import io
from datetime import datetime

API_KEY = "10bfb1374d5340fab47165420252801"  # Your WeatherAPI key
BASE_URL = "https://api.weatherapi.com/v1/forecast.json"

def get_weather_icon(icon_code):
    # WeatherAPI provides an icon code for the weather image
    icon_url = f"http:{icon_code}"  # WeatherAPI icon URL starts with http: (no @2x.png)
    response = requests.get(icon_url)
    img_data = Image.open(io.BytesIO(response.content))
    img = ImageTk.PhotoImage(img_data)
    return img

def format_time(time_str):
    # Convert the time from the API (UTC) to a 12-hour format for easier reading
    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    return time_obj.strftime("%I:%M %p")  # 12-hour format

def get_weather():
    city = city_entry.get()  # Get user input (city name)
    
    params = {
        "key": API_KEY,  # API Key parameter for WeatherAPI
        "q": city,
        "days": "10",  # Forecast for 10 days (1 day for current weather, 9 for forecast)
        "aqi": "no"  # Optional: 'no' to disable air quality data
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if location is valid
        if "location" in data:
            temp = data['current']['temp_c']  # Current temperature in Celsius
            humidity = data['current']['humidity']  # Humidity percentage
            description = data['current']['condition']['text']  # Weather description
            icon_code = data['current']['condition']['icon']  # Icon URL code
            
            wind_speed = data['current']['wind_kph']  # Wind speed in km/h
            wind_dir = data['current']['wind_dir']  # Wind direction

            # Fetch sunrise and sunset from the forecast part of the API
            astro = data['forecast']['forecastday'][0]['astro']
            sunrise = astro.get('sunrise', 'N/A')  # Sunrise time (if available)
            sunset = astro.get('sunset', 'N/A')    # Sunset time (if available)

            # Fetch UV index (feature 8)
            uv_index = data['current'].get('uv', 'N/A')  # UV index if available

            # Fetch 10-day forecast (Feature 10)
            forecast_data = data['forecast']['forecastday']
            forecast_labels = []
            for day in forecast_data[1:]:  # Skip the first entry as it is current weather
                date = day['date']
                max_temp = day['day']['maxtemp_c']
                min_temp = day['day']['mintemp_c']
                forecast_desc = day['day']['condition']['text']
                forecast_icon_code = day['day']['condition']['icon']
                forecast_icon = get_weather_icon(forecast_icon_code)

                forecast_labels.append({
                    'date': date,
                    'max_temp': max_temp,
                    'min_temp': min_temp,
                    'forecast_desc': forecast_desc,
                    'forecast_icon': forecast_icon
                })

            # Update the result window
            result_window = tk.Toplevel(root)
            result_window.title("Weather App")
            result_window.geometry("350x750")  # Increased height to accommodate more data
            result_window.configure(bg="white")
            
            # Weather icon (current weather)
            icon = get_weather_icon(icon_code)
            icon_label = tk.Label(result_window, image=icon, bg="white")
            icon_label.image = icon  # Keep a reference to the image
            icon_label.pack(pady=20)
            
            # Temperature (current weather)
            temp_label = tk.Label(result_window, text=f"{temp}°C", font=("Arial", 36, "bold"), bg="white")
            temp_label.pack()

            # Description (current weather)
            desc_label = tk.Label(result_window, text=description, font=("Arial", 14), bg="white")
            desc_label.pack()
            
            # Location
            location_label = tk.Label(result_window, text=f"Location: {data['location']['name']}, {data['location']['region']}", font=("Arial", 12), bg="white")
            location_label.pack(pady=10)
            
            # Humidity
            humidity_label = tk.Label(result_window, text=f"Humidity: {humidity}%", font=("Arial", 12), bg="white")
            humidity_label.pack()

            # Wind Speed and Direction
            wind_label = tk.Label(result_window, text=f"Wind: {wind_speed} km/h, {wind_dir}", font=("Arial", 12), bg="white")
            wind_label.pack()

            # Sunrise and Sunset
            sunrise_label = tk.Label(result_window, text=f"Sunrise: {sunrise}", font=("Arial", 12), bg="white")
            sunrise_label.pack(pady=5)
            sunset_label = tk.Label(result_window, text=f"Sunset: {sunset}", font=("Arial", 12), bg="white")
            sunset_label.pack(pady=5)

            # UV Index (Feature 8)
            uv_label = tk.Label(result_window, text=f"UV Index: {uv_index}", font=("Arial", 12), bg="white")
            uv_label.pack(pady=5)

            # 10-Day Forecast (Feature 10)
            forecast_title_label = tk.Label(result_window, text="10-Day Forecast", font=("Arial", 16, "bold"), bg="white")
            forecast_title_label.pack(pady=10)

            for forecast in forecast_labels:
                forecast_label = tk.Label(result_window, text=f"{forecast['date']}: {forecast['max_temp']}°C/{forecast['min_temp']}°C, {forecast['forecast_desc']}",
                                          font=("Arial", 12), bg="white")
                forecast_label.pack()

        else:
            result_label.config(text="Location not found", fg="red")
    else:
        result_label.config(text="Error: Unable to fetch weather data", fg="red")

# Create the main window
root = tk.Tk()
root.title("Weather App")
root.geometry("350x200")
root.configure(bg="white")

# Create and pack the title label
title_label = tk.Label(root, text="Weather App", font=("Arial", 16, "bold"), bg="white")
title_label.pack(pady=10)

# Create and pack the input frame
input_frame = tk.Frame(root, bg="white")
input_frame.pack(pady=10)

# City input
city_label = tk.Label(input_frame, text="Enter city name:", bg="white")
city_label.grid(row=0, column=0, padx=5, pady=5)
city_entry = tk.Entry(input_frame)
city_entry.grid(row=0, column=1, padx=5, pady=5)

# Get weather button
get_weather_button = ttk.Button(root, text="Get Weather", command=get_weather)
get_weather_button.pack(pady=10)

# Result label (for error messages)
result_label = tk.Label(root, text="", font=("Arial", 12), bg="white", fg="red")
result_label.pack(pady=10)

# Start the GUI event loop
root.mainloop()

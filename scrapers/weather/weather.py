import requests

def get_weather_data(location):
    url = f"http://api.weatherstack.com/current?access_key=b75917f665b4ef6e477e2c40ded63720&query={location}"
    
    response = requests.get(url)
    datalist = []
    
    if response.status_code == 200:
        try:
            weather_data = response.json()
            
            if "location" in weather_data and "current" in weather_data:
                weather = {
                    "City": weather_data["location"].get("name", ""),
                    "Country": weather_data["location"].get("country", ""),
                    "Region": weather_data["location"].get("region", ""),
                    "Local_Time": weather_data["location"].get("localtime", ""),
                    "Temperature": weather_data["current"].get("temperature", 0),
                    "Weather": weather_data["current"]["weather_descriptions"][0] if weather_data["current"].get("weather_descriptions") else "Unknown",
                    "Wind_Speed": weather_data["current"].get("wind_speed", 0),
                    "Wind_Direction": weather_data["current"].get("wind_dir", ""),
                    "Humidity": weather_data["current"].get("humidity", 0),
                    "Pressure_hPa": weather_data["current"].get("pressure", 0),
                    "Precipitation": weather_data["current"].get("precip", 0),
                    "Cloud_Cover": weather_data["current"].get("cloudcover", 0),
                    "Feels_Like": weather_data["current"].get("feelslike", 0),
                    "Visibility": weather_data["current"].get("visibility", 0)
                }

                datalist.append(weather)

        except Exception as e:
            pass

    return datalist if datalist else None

def main(location):
    location = location.strip().replace(' ', '+')
    data = get_weather_data(location)
    if data and isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return data
    else:
        return []  
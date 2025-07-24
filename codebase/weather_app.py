import requests
import os

def get_current_weather(city: str, api_key: str):
    """
    Fetches current weather information for a given city using WeatherAPI.com.

    Args:
        city (str): The name of the city.
        api_key (str): Your API key for WeatherAPI.com.

    Returns:
        dict: A dictionary containing weather information, or None if an error occurs.
    """
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "current" in data and "location" in data:
            location = data["location"]["name"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            temp_f = data["current"]["temp_f"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            last_updated = data["current"]["last_updated"]

            return {
                "city": location,
                "country": country,
                "temperature_celsius": temp_c,
                "temperature_fahrenheit": temp_f,
                "condition": condition,
                "humidity": humidity,
                "wind_kph": wind_kph,
                "last_updated": last_updated
            }
        else:
            print(f"Error: Unexpected response format for city '{city}'.")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} for city '{city}' (Status: {response.status_code}, Response: {response.text})")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err} for city '{city}'")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err} for city '{city}'")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err} for city '{city}'")
        return None
    except ValueError as json_err:
        print(f"JSON decoding error: {json_err} for city '{city}' (Response: {response.text})")
        return None

if __name__ == "__main__":
    # It's highly recommended to set your WeatherAPI.com API key as an environment variable
    # For example: export WEATHER_API_KEY="YOUR_API_KEY_HERE"
    
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        print("Error: WEATHER_API_KEY environment variable not set.")
        print("Please obtain a free API key from https://www.weatherapi.com/ and set it.")
    else:
        cities = ["London", "New York", "Tokyo", "Mumbai", "Global"]

        for city in cities:
            weather_data = get_current_weather(city, api_key)
            if weather_data:
                print(f"\n--- Current Weather in {weather_data['city']}, {weather_data['country']} ---")
                print(f"Last Updated: {weather_data['last_updated']}")
                print(f"Temperature: {weather_data['temperature_celsius']:.1f}°C / {weather_data['temperature_fahrenheit']:.1f}°F")
                print(f"Condition: {weather_data['condition']}")
                print(f"Humidity: {weather_data['humidity']}% ")
                print(f"Wind Speed: {weather_data['wind_kph']:.1f} kph")
            else:
                print(f"\nCould not retrieve weather for {city}.")

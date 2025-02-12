import requests
import boto3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# 1) Construct the path to your .env file
env_path = Path(__file__).parent / 'config.env'
# Example: If your .env file is at: test_weather/config.env/.env

# 2) Load the .env file
load_dotenv(dotenv_path=env_path)

# WeatherAPI Configuration
API_KEY = os.getenv('API_KEY')
BASE_URL = "http://api.weatherapi.com/v1/current.json"
CITIES = ["San Francisco", "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Indianapolis", "Columbus"]

# 3) Access the variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
# Initialize S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def fetch_weather_data(city):
    url = f"{BASE_URL}?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"],
            "precipitation_mm": data["current"].get("precip_mm", 0),
            "cloud_cover": data["current"].get("cloud", 0),
            "uv_index": data["current"].get("uv", 0),
            "timestamp": data["location"]["localtime"]
        }
        return weather_data
    else:
        print(f"Error fetching data for {city}: {response.status_code}")
        return None

# Fetch and upload data
def upload_weather_data():
    all_weather_data = []
    for city in CITIES:
        data = fetch_weather_data(city)
        if data:
            all_weather_data.append(data)

    # Convert to JSON and upload to S3
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"weather_data_{timestamp}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"raw/{file_name}",
        Body=json.dumps(all_weather_data),
        ContentType="application/json"
    )
    print(f"Uploaded weather data to S3: {file_name}")

upload_weather_data()

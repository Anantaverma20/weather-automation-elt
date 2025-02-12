import requests
import json
import boto3
import datetime
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
US_CITIES = {
    "Alabama": ["Birmingham", "Montgomery", "Huntsville"],
    "Alaska": ["Anchorage", "Juneau", "Fairbanks"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Williams"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville"],
    "California": ["Los Angeles", "San Francisco", "San Diego"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora"],
    "Connecticut": ["Bridgeport", "New Haven", "Stamford"],
    "Delaware": ["Wilmington", "Dover", "Newark"],
    "Florida": ["Miami", "Orlando", "Tampa"],
    "Georgia": ["Atlanta", "Augusta", "Columbus"],
    "Hawaii": ["Honolulu", "Hilo", "Kailua"],
    "Nevada": ["Las Vagas", "Reno", "Incline Village"],
    "Texas": ['Dalas', 'Austin', 'Houston'],
    "Washington":['Seattle','Tacoma', 'Vancouver'],
    "Illinois":['Chicago','Illinois City', 'Peoria'],
    "Michigan":['Detroit','Flint', 'Warren']
}


# 3) Access the variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
RAW_FOLDER = "raw/"

# Initialize S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def fetch_weather_data():
    data = []
    for state, cities in US_CITIES.items():
        for city in cities:
            response = requests.get(
                BASE_URL,
                params={"key": API_KEY, "q": city}
            )
            if response.status_code == 200:
                city_data = response.json()
                city_data.update({
                    "city": city,
                    "state": state,
                    "fetch_timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature": city_data["current"]["temp_c"],
                    "humidity": city_data["current"]["humidity"],
                    "rainfall": city_data.get("current", {}).get("precip_mm", 0),
                    "visibility": city_data["current"]["vis_km"],
                    "wind_speed": city_data["current"]["wind_kph"],
                    "condition": city_data["current"]["condition"]["text"],

                })
                data.append(city_data)
            else:
                print(f"Failed to fetch data for {city}: {response.status_code}")
    return data

def upload_to_s3(data):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{RAW_FOLDER}weather_data_{timestamp}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=file_name,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    print(f"Uploaded raw data to S3: {file_name}")

def lambda_handler(event, context):
    data = fetch_weather_data()
    upload_to_s3(data)
    return {"statusCode": 200, "body": "Weather data fetched and uploaded successfully."}

if __name__ == "__main__":
    try:
        data = fetch_weather_data()
        upload_to_s3(data)
    except Exception as e:
        print(f"Error: {str(e)}")

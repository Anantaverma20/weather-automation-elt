import streamlit as st
import boto3
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
from pathlib import Path

# 1) Construct the path to your .env file
env_path = Path(__file__).parent / 'config.env'
# Example: If your .env file is at: test_weather/config.env/.env

# 2) Load the .env file
load_dotenv(dotenv_path=env_path)

# 3) Access the variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
TRANSFORMED_FOLDER = "transformed/"
LATEST_FILE = "transformed/weather_data_transformed_2024-12-11_17-47-43.csv"

# Connect to S3
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

# Fetch the latest transformed file from S3
def fetch_transformed_data():
    s3 = get_s3_client()
    key = f"{TRANSFORMED_FOLDER}{LATEST_FILE}"
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Streamlit App Layout
st.title("Real-Time Weather Data Dashboard")
st.markdown("This dashboard visualizes weather data fetched and transformed from S3.")

# Fetch data
data = fetch_transformed_data()

# If data is available, display it
if not data.empty:
    st.subheader("Weather Data Table")
    st.dataframe(data)

    # Select city or state for filtering
    city = st.selectbox("Select City", data["city"].unique())
    state = st.selectbox("Select State", data["state"].unique())

    # Filtered data
    filtered_data = data[(data["city"] == city) & (data["state"] == state)]
    st.subheader(f"Weather Details for {city}, {state}")
    st.dataframe(filtered_data)

    # Plot temperature and humidity
    st.subheader("Temperature and Humidity Trends")
    st.line_chart(filtered_data[["temperature_c", "humidity"]])

else:
    st.warning("No data available to display.")


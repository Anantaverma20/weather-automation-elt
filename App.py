import boto3
import pandas as pd
from io import StringIO
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
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


def fetch_transformed_data():
    """Fetch the latest transformed weather data CSV from S3."""
    # Initializing the S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        # List objects in the "transformed/" folder
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=TRANSFORMED_FOLDER)

        # Check if the folder has any files
        if "Contents" not in response:
            st.error("No files found in the 'transformed' folder.")
            return pd.DataFrame()

        # Find the latest file by LastModified timestamp
        latest_file = max(response["Contents"], key=lambda x: x["LastModified"])["Key"]

        # Fetch the latest file
        response = s3.get_object(Bucket=S3_BUCKET, Key=latest_file)
        csv_data = response["Body"].read().decode("utf-8")

        # Load CSV data into a Pandas DataFrame
        df = pd.read_csv(StringIO(csv_data))
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Streamlit App
st.title("Real-Time Weather Data Dashboard")
st.write("Comparative visualizations of weather data fetched and transformed from S3.")

# Fetch data
data = fetch_transformed_data()

if not data.empty:
    # Display raw data
    st.subheader("Weather Data Table")
    st.dataframe(data)

    # Overview Metrics
    st.subheader("Weather Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Temperature (°C)", round(data["temperature_c"].mean(), 2))
    col2.metric("Avg Humidity (%)", round(data["humidity"].mean(), 2))
    col3.metric("Total Rainfall (mm)", round(data["rainfall_mm"].sum(), 2))
    col4.metric("Avg Wind Speed (kph)", round(data["wind_kph"].mean(), 2))

    # City-wise Comparisons
    st.subheader("City-wise Weather Comparisons")
    parameter = st.selectbox("Select a Parameter for Comparison", ["temperature_c", "humidity", "rainfall_mm", "wind_kph"])
    plt.figure(figsize=(14, 8))
    sns.barplot(data=data, x="city", y=parameter, palette="viridis", ci=None, order=data.groupby("city")[parameter].mean().sort_values(ascending=False).index)
    plt.title(f"City-wise Comparison of {parameter.capitalize()}", fontsize=16)
    plt.xlabel("City", fontsize=12)
    plt.ylabel(parameter.capitalize(), fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    st.pyplot(plt.gcf())
    plt.clf()

    # State-wise Trends
    st.subheader("State-wise Weather Trends")
    trend_parameter = st.selectbox("Select a Trend Parameter", ["temperature_c", "humidity", "rainfall_mm", "wind_kph"])
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=data, x="timestamp", y=trend_parameter, hue="state", marker="o", palette="Set2")
    plt.title(f"State-wise {trend_parameter.capitalize()} Trends Over Time", fontsize=16)
    plt.xlabel("Timestamp", fontsize=12)
    plt.ylabel(trend_parameter.capitalize(), fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title="State", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(plt.gcf())
    plt.clf()

    # Heatmap for Attribute Correlations
    st.subheader("Correlation Heatmap of Weather Attributes")
    heatmap_data = data[["temperature_c", "humidity", "rainfall_mm", "wind_kph"]]
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data.corr(), annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title("Correlation Heatmap", fontsize=16)
    st.pyplot(plt.gcf())
    plt.clf()

    # State-wise Aggregate Data (Grouped Bar Chart)
    st.subheader("State-wise Aggregate Data")
    agg_parameter = st.selectbox("Select a Parameter to Aggregate", ["temperature_c", "humidity", "rainfall_mm", "wind_kph"])
    agg_data = data.groupby("state")[agg_parameter].mean().reset_index().sort_values(by=agg_parameter, ascending=False)
    plt.figure(figsize=(14, 8))
    sns.barplot(data=agg_data, x="state", y=agg_parameter, palette="muted", ci=None)
    plt.title(f"State-wise Average {agg_parameter.capitalize()}", fontsize=16)
    plt.xlabel("State", fontsize=12)
    plt.ylabel(f"Avg {agg_parameter.capitalize()}", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    st.pyplot(plt.gcf())
    plt.clf()

else:
    st.warning("No data available to display.")
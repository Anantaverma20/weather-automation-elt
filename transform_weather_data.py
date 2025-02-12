import boto3
import json
import pandas as pd
from io import StringIO
import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# 1) Construct the path to your .env file
env_path = Path(__file__).parent / 'config.env'


# 2) Load the .env file
load_dotenv(dotenv_path=env_path)

# 3) Access the variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
RAW_FOLDER = "raw/"
TRANSFORMED_FOLDER = "transformed/"

# Initialize the S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


# Function to transform data
def transform_data():
    try:
        # Fetch the latest raw data file from S3
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=RAW_FOLDER)
        if "Contents" not in response or len(response["Contents"]) == 0:
            raise Exception("No files found in the raw data folder.")

        # Get the latest file
        latest_file = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]["Key"]
        print(f"Processing file: {latest_file}")

        # Fetch the content of the file
        response = s3.get_object(Bucket=S3_BUCKET, Key=latest_file)
        raw_data = json.loads(response['Body'].read().decode('utf-8'))

        # Transform the data
        transformed_data = []
        for entry in raw_data:
            transformed_data.append({
                "city": entry["city"],
                "state": entry["state"],
                "temperature_c": entry["temperature"],
                "humidity": entry["humidity"],
                "wind_kph": entry["wind_speed"],
                "rainfall_mm": entry["rainfall"],
                "visibility_km": entry["visibility"],
                "condition": entry["condition"],
                "timestamp": entry["fetch_timestamp"]
            })

        # Convert to CSV
        df = pd.DataFrame(transformed_data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        # Generate a unique timestamp for the transformed file
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        transformed_file_name = f"{TRANSFORMED_FOLDER}weather_data_transformed_{timestamp}.csv"

        # Upload transformed data to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=transformed_file_name,
            Body=csv_buffer.getvalue(),
            ContentType="text/csv"
        )
        print(f"Transformed data saved to S3 as {transformed_file_name}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Run the function
if __name__ == "__main__":
    transform_data()

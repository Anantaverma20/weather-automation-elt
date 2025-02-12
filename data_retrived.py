import boto3
import json

# Initialize S3 client
s3 = boto3.client('s3')

# Configuration
S3_BUCKET = "dataengineeringweatherdata"
RAW_FOLDER = "raw/"
TRANSFORMED_FOLDER = "transformed/"

def transform_data():
    # List all objects in the raw folder
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=RAW_FOLDER)
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith(".json"):
            raw_data = s3.get_object(Bucket=S3_BUCKET, Key=key)
            data = json.loads(raw_data['Body'].read())
            # Perform your transformation here
            transformed_data = [{"city": d["city"], "state": d["state"], "temp": d["current"]["temp_c"]} for d in data]
            # Save the transformed data to S3
            new_key = key.replace(RAW_FOLDER, TRANSFORMED_FOLDER)
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=new_key,
                Body=json.dumps(transformed_data),
                ContentType="application/json"
            )
            print(f"Transformed data uploaded to S3: {new_key}")

if __name__ == "__main__":
    transform_data()

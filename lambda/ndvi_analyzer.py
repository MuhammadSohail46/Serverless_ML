import boto3
import os
import numpy as np
import rasterio
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
sns = boto3.client('sns')

bucket = os.environ.get("BUCKET_NAME", "ndvi-agri-input")
threshold = float(os.environ.get("NDVI_THRESHOLD", 0.4))
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]  # Must be set in Lambda env

def download_band(key, filename):
    s3.download_file(bucket, key, filename)
    return filename

def compute_ndvi(nir_path, red_path):
    with rasterio.open(nir_path) as nir_src, rasterio.open(red_path) as red_src:
        nir = nir_src.read(1).astype(float)
        red = red_src.read(1).astype(float)

        ndvi = (nir - red) / (nir + red + 1e-6)
        ndvi = np.clip(ndvi, -1, 1)
        return ndvi

def lambda_handler(event, context):
    print("Event:", event)

    # Parse key from S3 event
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    base_path = os.path.dirname(key)
    print("Base path:", base_path)

    # Define keys
    red_key = f"{base_path}/red.tif"
    nir_key = f"{base_path}/nir.tif"

    # Download to /tmp
    red_path = "/tmp/red.tif"
    nir_path = "/tmp/nir.tif"
    download_band(red_key, red_path)
    download_band(nir_key, nir_path)

    # Compute NDVI
    ndvi = compute_ndvi(nir_path, red_path)
    avg_ndvi = np.nanmean(ndvi)
    print(f"Avg NDVI = {avg_ndvi:.4f}")

    # If below threshold, send alert
    if avg_ndvi < threshold:
        message = f"🌱 ALERT: Crop stress detected in {base_path}\nAvg NDVI = {avg_ndvi:.3f}"
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Crop Stress Alert"
        )
        print("Alert sent.")
    else:
        print("NDVI healthy. No alert sent.")

    return {
        "statusCode": 200,
        "body": f"NDVI calculated: {avg_ndvi:.4f}"
    }

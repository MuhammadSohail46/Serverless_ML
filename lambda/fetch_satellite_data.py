import json
import boto3
from datetime import datetime, timedelta
from shapely import wkt
from shapely.geometry import mapping
from pystac_client import Client
import rasterio
from rasterio.session import AWSSession
import os

# AWS setup
s3 = boto3.client('s3')
region = 'us-east-1'
bucket = 'ndvi-agri-input'  # Replace with your bucket name

# WKT polygon for the field (Islamabad region)
WKT_POLYGON = """POLYGON((
  73.0358 33.7434,
  73.0500 33.7434,
  73.0500 33.7555,
  73.0440 33.7630,
  73.0350 33.7610,
  73.0300 33.7540,
  73.0310 33.7470,
  73.0358 33.7434
))""" 

# Polygon is Hardcoded for Now.

def lambda_handler(event, context):
    polygon = wkt.loads(WKT_POLYGON)
    geojson_geom = mapping(polygon)

    client = Client.open("https://earth-search.aws.element84.com/v1")

    # Get recent imagery (last 7 days)
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    search = client.search(
        collections=["sentinel-2-l2a"],
        intersects=geojson_geom,
        datetime=f"{start_date.isoformat()}/{today.isoformat()}",
        query={"eo:cloud_cover": {"lt": 10}},
        sortby=[{"field": "properties.datetime", "direction": "desc"}],
        max_items=1
    )

    items = list(search.items())
    if not items:
        print("No suitable imagery found.")
        return {"statusCode": 404, "body": "No satellite imagery found"}

    item = items[0]
    date_str = item.datetime.strftime("%Y-%m-%d")
    prefix = f"field-demo/{date_str}"

    session = boto3.Session(region_name=region)
    aws_session = AWSSession(session)

    for asset_key, band_name in [("red", "red"), ("nir", "nir")]:
        href = item.assets[asset_key].href
        with rasterio.Env(aws_session):
            with rasterio.open(href) as src:
                data = src.read(1)
                profile = src.profile
                profile.update(compress='lzw')

                tmp_file = f"/tmp/{band_name}.tif"
                with rasterio.open(tmp_file, "w", **profile) as dst:
                    dst.write(data, 1)

                s3_key = f"{prefix}/{band_name}.tif"
                s3.upload_file(tmp_file, bucket, s3_key)
                print(f"Uploaded: {s3_key}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Sentinel-2 bands downloaded successfully.",
            "s3_prefix": prefix
        })
    }

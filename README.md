# AgriPulse: Serverless Crop Stress Detector

AgriPulse is a fully serverless geospatial pipeline that detects crop stress using NDVI (Normalized Difference Vegetation Index) from Sentinel-2 satellite imagery. Built with AWS Lambda, EventBridge, S3, and SNS, it empowers farmers and analysts to monitor vegetation health and receive alerts when signs of stress appear — automatically, and without infrastructure.

---

## 🚀 What It Does

- Fetches recent Sentinel-2 imagery daily for a defined field polygon (WKT format)
- Downloads the **Red** and **NIR** bands and stores them in Amazon S3
- Calculates NDVI using a triggered Lambda function
- Sends crop stress alerts via Amazon SNS if average NDVI is below a safe threshold

---

## 🔁 Architecture Flow

```
EventBridge (daily trigger)
     ↓
Lambda: fetch_satellite_data.py
     ↓
Downloads Sentinel-2 bands (red & NIR) using STAC API
     ↓
Uploads bands to Amazon S3
     ↓ (S3 Trigger)
Lambda: ndvi_analyzer.py
     ↓
Calculates NDVI using rasterio & numpy
     ↓
Sends alert via SNS if NDVI < threshold
```

---

## 🛠️ Technologies Used

**Languages & Libraries**  
Python, rasterio, numpy, shapely, pystac-client, boto3

**AWS Services**  
AWS Lambda, Amazon S3, Amazon EventBridge, Amazon SNS, AWS IAM, Amazon CloudWatch

**Deployment**  
Serverless Framework (Infrastructure as Code)

---

## 🧪 How to Test

1. Clone the repo  
2. Install dependencies (or package using Docker for rasterio/shapely)
3. Deploy using Serverless Framework:
   ```bash
   sls deploy
   ```
4. (Optional) Trigger the satellite fetch Lambda manually:
   ```bash
   sls invoke -f fetchSatelliteData
   ```

You should see `.tif` files appear in your S3 bucket. These will trigger the NDVI analyzer Lambda and send alerts if stress is detected.

---

## 📦 Folder Structure

```
.
├── fetch_satellite_data.py   # Lambda to download Sentinel-2 Red/NIR bands
├── ndvi_analyzer.py          # Lambda to compute NDVI and send alerts
├── serverless.yml            # IaC deployment config (2 functions + triggers)
├── requirements.txt          # Lambda dependencies
├── README.md                 # You're here!
```


---

## ✅ How AgriPulse Uses AWS Lambda

AWS Lambda is the core execution engine in AgriPulse. Two Lambda functions power the entire pipeline:

1. **fetch_satellite_data.py**:  
   Triggered daily by Amazon EventBridge, this Lambda fetches recent Sentinel-2 satellite imagery using the STAC API, selects the appropriate Red and NIR bands, and uploads them to Amazon S3. This function automates satellite data acquisition for the defined field polygon.

2. **ndvi_analyzer.py**:  
   Triggered automatically by S3 when new `.tif` files are uploaded. It downloads the Red and NIR bands, computes NDVI using rasterio and numpy, and sends an alert via Amazon SNS if the average NDVI indicates possible crop stress. This Lambda ensures near real-time crop monitoring and alerting.

By using AWS Lambda, AgriPulse remains fully serverless, cost-effective, and scalable without needing any EC2 instances or persistent infrastructure.

---

## 💡 Future Enhancements

- Generate visual NDVI heatmaps and save them to S3
- Add field selection and GeoJSON support via API Gateway
- Integrate Bedrock or SageMaker for disease/pest detection
- Build a web/mobile dashboard for farmer alerts

---

## 📄 License

This project is open-source under the MIT License.
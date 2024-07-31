from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
from azure.storage.blob import BlobServiceClient, ContentSettings
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from loguru import logger
from io import BytesIO
import logging
import time
import urllib.parse
import os

# Loading Environment variables (Azure Storage Account Name and Key)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('AZURE_CONTAINER_NAME')

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Prometheus Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total number of HTTP requests", labelnames=["method", "endpoint"])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        response = await call_next(request)
        return response

app.add_middleware(PrometheusMiddleware)

# Loki Logger Configuration
class LokiHandler(logging.Handler):
    def __init__(self, url, tags=None, version="1"):
        super().__init__()
        self.url = url
        self.tags = tags or {}
        self.version = version

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "streams": [
                {
                    "stream": self.tags,
                    "values": [[str(int(time.time() * 1000)), log_entry]]
                }
            ]
        }
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send log to Loki: {e}")

loki_url = "http://192.168.1.255:3100/loki/api/v1/push"  # Update to your Loki URL
loki_handler = LokiHandler(url=loki_url, tags={"application": "fastapi-app"})

logger.add(loki_handler, format="{message}")

@app.post("/generate-qr/")
async def generate_qr(url: str):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name for Blob Storage
    encoded_url = urllib.parse.quote(url, safe='')
    file_name = f"qr_codes/{encoded_url}.png"
    
    try:
        # Upload to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.upload_blob(img_byte_arr, blob_type="BlockBlob", content_settings=ContentSettings(content_type='image/png'))

        logger.info(f"QR code generated for URL: {url}")

        # Generate the Blob URL
        blob_url = blob_client.url
        return {"qr_code_url": blob_url}
    except Exception as e:
        logger.error(f"Error generating QR code for URL: {url} - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST) #prometheus url

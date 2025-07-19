import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.environ.get("POSTGRESQL_PASSWORD")

DB_HOST = os.environ.get("POSTGRESQL_HOST")
DB_PORT = os.environ.get("POSTGRESQL_PORT")
DB_NAME = os.environ.get("POSTGRESQL_DBNAME")
DB_USER = os.environ.get("POSTGRESQL_USER")
DB_PASS = os.environ.get("POSTGRESQL_PASSWORD")


S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

FREEDOM_MERCHANT_ID =  os.environ.get("FREEDOM_MERCHANT_ID")
FREEDOM_SECRET_KEY =  os.environ.get("FREEDOM_SECRET_KEY")
FREEDOM_ENDPOINT =  os.environ.get("FREEDOM_ENDPOINT")
FREEDOM_FRONTEND_URL = os.environ.get("FREEDOM_FRONTEND_URL")
FREEDOM_BACKEND_URL = os.environ.get("FREEDOM_BACKEND_URL")


SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin]

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT")
RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST")
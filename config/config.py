import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.environ.get("POSTGRESQL_PASSWORD")

DB_HOST = os.environ.get("POSTGRESQL_HOST")
DB_PORT = os.environ.get("POSTGRESQL_PORT")
DB_NAME = os.environ.get("POSTGRESQL_DBNAME")
DB_USER = os.environ.get("POSTGRESQL_USER")
DB_PASS = os.environ.get("POSTGRESQL_PASSWORD")


ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
ENDPOINT_URL = os.environ.get("ENDPOINT_URL")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

MERCHANT_ID =  os.environ.get("MERCHANT_ID")
SECRET_KEY =  os.environ.get("SECRET_KEY")
ENDPOINT =  os.environ.get("ENDPOINT")
FRONTEND_URL = os.environ.get("FRONTEND_URL")
BACKEND_URL = os.environ.get("FRONTEND_URL")


SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")



origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin]
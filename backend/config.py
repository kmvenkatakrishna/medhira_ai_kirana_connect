import os

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# DynamoDB Table Names
STORES_TABLE = os.getenv("STORES_TABLE", "kirana_stores")
PRODUCTS_TABLE = os.getenv("PRODUCTS_TABLE", "kirana_products")
INVENTORY_TABLE = os.getenv("INVENTORY_TABLE", "kirana_inventory")
TRANSACTIONS_TABLE = os.getenv("TRANSACTIONS_TABLE", "kirana_transactions")
ORDERS_TABLE = os.getenv("ORDERS_TABLE", "kirana_orders")
PREDICTIONS_TABLE = os.getenv("PREDICTIONS_TABLE", "kirana_predictions")
DISTRIBUTORS_TABLE = os.getenv("DISTRIBUTORS_TABLE", "kirana_distributors")

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "kirana-connect-media")

# Application Settings
APP_NAME = "KiranaConnect AI"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Use local mode (in-memory data) when DynamoDB is not available
USE_LOCAL_DATA = os.getenv("USE_LOCAL_DATA", "true").lower() == "true"

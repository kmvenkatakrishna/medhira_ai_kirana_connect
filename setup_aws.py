"""
AWS Setup Script — Creates all required AWS resources for KiranaConnect.
Run: python setup_aws.py
"""
import boto3
import json
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))
from backend.config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

print(f"Region: {AWS_REGION}")
print(f"Key ID: {AWS_ACCESS_KEY_ID[:10]}..." if AWS_ACCESS_KEY_ID else "No key!")


def get_client(service):
    return boto3.client(
        service,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )


def get_resource(service):
    return boto3.resource(
        service,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )


# ================================================================
#  1. CREATE DYNAMODB TABLES
# ================================================================

TABLES = [
    {
        "TableName": "kirana_stores",
        "KeySchema": [{"AttributeName": "store_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "store_id", "AttributeType": "S"}],
    },
    {
        "TableName": "kirana_products",
        "KeySchema": [{"AttributeName": "product_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "product_id", "AttributeType": "S"}],
    },
    {
        "TableName": "kirana_inventory",
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "product_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "product_id", "AttributeType": "S"},
        ],
    },
    {
        "TableName": "kirana_transactions",
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "transaction_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "transaction_id", "AttributeType": "S"},
        ],
    },
    {
        "TableName": "kirana_orders",
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "order_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "order_id", "AttributeType": "S"},
        ],
    },
    {
        "TableName": "kirana_predictions",
        "KeySchema": [
            {"AttributeName": "store_id", "KeyType": "HASH"},
            {"AttributeName": "product_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "store_id", "AttributeType": "S"},
            {"AttributeName": "product_id", "AttributeType": "S"},
        ],
    },
    {
        "TableName": "kirana_distributors",
        "KeySchema": [{"AttributeName": "distributor_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "distributor_id", "AttributeType": "S"}],
    },
]


def create_dynamodb_tables():
    dynamodb = get_client("dynamodb")
    existing = dynamodb.list_tables()["TableNames"]
    print(f"\nExisting DynamoDB tables: {existing}")

    for table_def in TABLES:
        name = table_def["TableName"]
        if name in existing:
            print(f"  [SKIP] {name} already exists")
            continue
        try:
            dynamodb.create_table(
                TableName=name,
                KeySchema=table_def["KeySchema"],
                AttributeDefinitions=table_def["AttributeDefinitions"],
                BillingMode="PAY_PER_REQUEST",  # No provisioning needed
            )
            print(f"  [OK] Created table: {name}")
        except Exception as e:
            print(f"  [ERR] Failed to create {name}: {e}")

    # Wait for tables to become active
    print("\nWaiting for tables to become ACTIVE...")
    for table_def in TABLES:
        name = table_def["TableName"]
        try:
            waiter = dynamodb.get_waiter("table_exists")
            waiter.wait(TableName=name, WaiterConfig={"Delay": 3, "MaxAttempts": 20})
            print(f"  [OK] {name} is ACTIVE")
        except Exception as e:
            print(f"  [WARN] {name}: {e}")


# ================================================================
#  2. CREATE S3 BUCKET
# ================================================================

def create_s3_bucket():
    s3 = get_client("s3")
    bucket_name = "kirana-connect-media"

    try:
        existing = [b["Name"] for b in s3.list_buckets()["Buckets"]]
        if bucket_name in existing:
            print(f"\n  [SKIP] S3 bucket '{bucket_name}' already exists")
            return
    except Exception as e:
        print(f"  [WARN] Could not list buckets: {e}")

    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
        )
        print(f"\n  [OK] Created S3 bucket: {bucket_name}")

        # Enable static website hosting
        s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                "IndexDocument": {"Suffix": "index.html"},
                "ErrorDocument": {"Key": "index.html"}
            }
        )
        print(f"  [OK] Static website hosting enabled")

        # Set public read policy for frontend
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }]
        }
        # Disable block public access first
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        print(f"  [OK] Public read policy set")

    except Exception as e:
        print(f"  [ERR] Failed to create bucket: {e}")


# ================================================================
#  3. UPLOAD FRONTEND FILES TO S3
# ================================================================

def upload_frontend_to_s3():
    s3 = get_client("s3")
    bucket_name = "kirana-connect-media"
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    content_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
    }

    print(f"\nUploading frontend files to s3://{bucket_name}/")
    file_count = 0

    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            filepath = os.path.join(root, file)
            # Relative key: e.g., "index.html", "css/styles.css"
            key = os.path.relpath(filepath, frontend_dir).replace("\\", "/")
            ext = os.path.splitext(file)[1].lower()
            ct = content_types.get(ext, "application/octet-stream")

            try:
                s3.upload_file(
                    filepath, bucket_name, key,
                    ExtraArgs={"ContentType": ct}
                )
                print(f"  [OK] {key}")
                file_count += 1
            except Exception as e:
                print(f"  [ERR] {key}: {e}")

    # Also upload presentation.html to root
    pres_path = os.path.join(os.path.dirname(__file__), "presentation.html")
    if os.path.exists(pres_path):
        s3.upload_file(pres_path, bucket_name, "presentation.html",
                      ExtraArgs={"ContentType": "text/html"})
        print(f"  [OK] presentation.html")
        file_count += 1

    print(f"\n  Total files uploaded: {file_count}")
    print(f"  Frontend URL: http://{bucket_name}.s3-website.{AWS_REGION}.amazonaws.com/")


# ================================================================
#  4. SEED DYNAMODB WITH DATA
# ================================================================

def seed_dynamodb():
    """Seed DynamoDB tables with the same synthetic data used locally."""
    dynamodb = get_resource("dynamodb")

    # Import the local data store to get the synthetic data
    from backend.services.data_store import data_store

    print("\nSeeding DynamoDB tables...")

    # Seed stores (list of dicts)
    stores_table = dynamodb.Table("kirana_stores")
    for store in data_store.stores:
        stores_table.put_item(Item=_convert_floats(store))
    print(f"  [OK] Stores: {len(data_store.stores)} items")

    # Seed products (list of dicts)
    products_table = dynamodb.Table("kirana_products")
    for product in data_store.products:
        products_table.put_item(Item=_convert_floats(product))
    print(f"  [OK] Products: {len(data_store.products)} items")

    # Seed inventory (dict: store_id -> list of items)
    inventory_table = dynamodb.Table("kirana_inventory")
    inv_count = 0
    for store_id, items in data_store.inventory.items():
        for item in items:
            inv_item = _convert_floats(item)
            inv_item["store_id"] = store_id
            inventory_table.put_item(Item=inv_item)
            inv_count += 1
    print(f"  [OK] Inventory: {inv_count} items")

    # Seed transactions (dict: store_id -> list of txns)
    txn_table = dynamodb.Table("kirana_transactions")
    txn_count = 0
    for store_id, txns in data_store.transactions.items():
        for txn in txns:
            item = _convert_floats(txn)
            item["store_id"] = store_id
            txn_table.put_item(Item=item)
            txn_count += 1
    print(f"  [OK] Transactions: {txn_count} items")

    # Seed distributors (list of dicts)
    dist_table = dynamodb.Table("kirana_distributors")
    for dist in data_store.distributors:
        dist_table.put_item(Item=_convert_floats(dist))
    print(f"  [OK] Distributors: {len(data_store.distributors)} items")

    print("\n[DONE] DynamoDB seeded successfully!")


def _convert_floats(obj):
    """Convert float values to strings/Decimal for DynamoDB compatibility."""
    from decimal import Decimal
    if isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats(v) for v in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj


# ================================================================
#  5. CHECK BEDROCK ACCESS
# ================================================================

def check_bedrock():
    try:
        bedrock = get_client("bedrock")
        models = bedrock.list_foundation_models(byProvider="Anthropic")
        print("\nBedrock Anthropic models available:")
        for m in models.get("modelSummaries", []):
            status = "ACTIVE" if m.get("modelLifecycle", {}).get("status") == "ACTIVE" else "?"
            print(f"  [{status}] {m['modelId']}: {m.get('modelName', '?')}")
    except Exception as e:
        print(f"\n  [WARN] Bedrock check failed: {e}")
        print("  You may need to enable Bedrock model access in AWS Console.")


# ================================================================
#  MAIN
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  KiranaConnect AWS Setup")
    print("=" * 60)

    print("\n[1/5] Creating DynamoDB tables...")
    create_dynamodb_tables()

    print("\n[2/5] Creating S3 bucket...")
    create_s3_bucket()

    print("\n[3/5] Uploading frontend to S3...")
    upload_frontend_to_s3()

    print("\n[4/5] Seeding DynamoDB with data...")
    seed_dynamodb()

    print("\n[5/5] Checking Bedrock access...")
    check_bedrock()

    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n  Frontend: http://kirana-connect-media.s3-website.{AWS_REGION}.amazonaws.com/")
    print(f"  DynamoDB: 7 tables in {AWS_REGION}")
    print(f"  Next: Set USE_LOCAL_DATA=false in .env to use DynamoDB")
    print()

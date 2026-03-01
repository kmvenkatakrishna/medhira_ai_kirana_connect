"""
Setup DynamoDB Tables for KiranaConnect AI.
Run this script to create all required DynamoDB tables in your AWS account.

Usage:
    python deploy/setup_dynamodb.py
"""

import boto3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import AWS_REGION

dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

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


def create_tables():
    existing = dynamodb.list_tables()["TableNames"]

    for table_config in TABLES:
        name = table_config["TableName"]
        if name in existing:
            print(f"  ⏭️  Table '{name}' already exists — skipping")
            continue

        try:
            dynamodb.create_table(
                TableName=name,
                KeySchema=table_config["KeySchema"],
                AttributeDefinitions=table_config["AttributeDefinitions"],
                BillingMode="PAY_PER_REQUEST",
            )
            print(f"  ✅ Created table '{name}'")
        except Exception as e:
            print(f"  ❌ Error creating '{name}': {e}")

    print("\n🎉 DynamoDB setup complete!")


if __name__ == "__main__":
    print("🔧 Setting up DynamoDB tables for KiranaConnect AI...")
    print(f"   Region: {AWS_REGION}\n")
    create_tables()

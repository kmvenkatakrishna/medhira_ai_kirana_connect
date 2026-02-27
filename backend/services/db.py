import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Get table names from env vars or defaults for local testing
INVENTORY_TABLE_NAME = os.environ.get("INVENTORY_TABLE", "KiranaInventory")
MESSAGES_TABLE_NAME = os.environ.get("MESSAGES_TABLE", "KiranaMessages")

use_mock_db = False
inventory_mock = []
messages_mock = []

# Use local dynamodb if running locally, otherwise use AWS
db_url = os.environ.get("DYNAMODB_URL", None)
try:
    if db_url:
        dynamodb = boto3.resource('dynamodb', endpoint_url=db_url)
    else:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Check if we have credentials by doing a dummy call
    boto3.client('sts').get_caller_identity()
    
    inventory_table = dynamodb.Table(INVENTORY_TABLE_NAME)
    messages_table = dynamodb.Table(MESSAGES_TABLE_NAME)
except Exception as e:
    print(f"AWS Credentials missing or invalid. Using Mock In-Memory Database for prototype. Reason: {e}")
    use_mock_db = True

class InventoryService:
    @staticmethod
    def get_inventory(store_id: str) -> List[Dict[str, Any]]:
        if use_mock_db:
            return [item for item in inventory_mock if item['store_id'] == store_id]
        try:
            response = inventory_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('store_id').eq(store_id)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting inventory: {e}")
            return []

    @staticmethod
    def get_item(store_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        if use_mock_db:
            for item in inventory_mock:
                if item['store_id'] == store_id and item['product_id'] == product_id:
                    return item
            return None
        try:
            response = inventory_table.get_item(
                Key={'store_id': store_id, 'product_id': product_id}
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error getting item: {e}")
            return None

    @staticmethod
    def add_or_update_item(store_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'product_id' not in item_data:
            item_data['product_id'] = str(uuid.uuid4())
        
        item_data['store_id'] = store_id
        item_data['last_updated'] = datetime.utcnow().isoformat()
        
        if use_mock_db:
            for i, item in enumerate(inventory_mock):
                if item['store_id'] == store_id and item['product_id'] == item_data['product_id']:
                    inventory_mock[i] = item_data
                    return item_data
            inventory_mock.append(item_data)
            return item_data

        try:
            inventory_table.put_item(Item=item_data)
            return item_data
        except Exception as e:
            print(f"Error saving item: {e}")
            raise e

    @staticmethod
    def delete_item(store_id: str, product_id: str) -> bool:
        if use_mock_db:
            global inventory_mock
            inventory_mock = [item for item in inventory_mock if not (item['store_id'] == store_id and item['product_id'] == product_id)]
            return True

        try:
            inventory_table.delete_item(
                Key={'store_id': store_id, 'product_id': product_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

class MessageService:
    @staticmethod
    def save_message(store_id: str, sender: str, message: str, intent: str = "unknown") -> Dict[str, Any]:
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'store_id': store_id,
            'timestamp': timestamp,
            'message_id': message_id,
            'sender': sender, # 'user' or 'bot'
            'message': message,
            'intent': intent
        }
        
        if use_mock_db:
            messages_mock.append(item)
            # sort inside mock
            messages_mock.sort(key=lambda x: x['timestamp'], reverse=True)
            return item

        try:
            messages_table.put_item(Item=item)
            return item
        except Exception as e:
            print(f"Error saving message: {e}")
            raise e
            
    @staticmethod
    def get_recent_messages(store_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if use_mock_db:
            store_msgs = [m for m in messages_mock if m['store_id'] == store_id]
            # Assumes messages_mock is sorted desc
            return store_msgs[:limit]

        try:
            response = messages_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('store_id').eq(store_id),
                ScanIndexForward=False, # Get newest first (assuming timestamp is sort key)
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

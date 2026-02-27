from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re
from services.db import MessageService, InventoryService

router = APIRouter()

class WhatsAppMessage(BaseModel):
    store_id: str
    sender: str
    text: str

def parse_intent(text: str):
    text = text.lower()
    if "buy" in text or "bought" in text or "add" in text:
        return "add_stock"
    if "check" in text or "stock" in text or "inventory" in text:
        return "check_stock"
    if "sell" in text or "sold" in text:
        return "reduce_stock"
    return "unknown"

def process_add_stock(store_id: str, text: str):
    # Very basic regex mock NLP for prototype: "Bought 10 milk packets"
    match = re.search(r'(?:bought|add)\s+(\d+)\s+([a-zA-Z\s]+)', text.lower())
    if match:
        qty = int(match.group(1))
        item_name = match.group(2).strip()
        
        # Check if item exists
        inventory = InventoryService.get_inventory(store_id)
        existing_item = next((item for item in inventory if item['name'].lower() == item_name), None)
        
        if existing_item:
            existing_item['quantity'] += qty
            InventoryService.add_or_update_item(store_id, existing_item)
            return f"Updated {item_name} stock. Added {qty}, total is now {existing_item['quantity']}."
        else:
            # Create new
            new_item = {
                "name": item_name.title(),
                "category": "Uncategorized",
                "quantity": qty,
                "unit_price": 0.0,
                "min_threshold": 5,
                "unit": "pcs"
            }
            InventoryService.add_or_update_item(store_id, new_item)
            return f"Added new item: {item_name.title()} with quantity {qty}."
    
    return "I couldn't understand the quantity and item. Please say something like 'Bought 50 milk packets'."

def process_check_stock(store_id: str, text: str):
    inventory = InventoryService.get_inventory(store_id)
    if not inventory:
        return "Your inventory is currently empty."
    
    # Check for specific item
    words = text.lower().split()
    for item in inventory:
        if item['name'].lower() in text.lower():
            return f"You have {item['quantity']} {item['unit']} of {item['name']} in stock."
            
    # Generic check
    low_stock = [i for i in inventory if i['quantity'] <= int(i.get('min_threshold', 10))]
    response = f"You have {len(inventory)} total items."
    if low_stock:
        response += f"\n\nAttention: {len(low_stock)} items are running low!"
        for item in low_stock:
            response += f"\n- {item['name']}: {item['quantity']} left"
            
    return response

@router.post("/message")
def simulate_whatsapp_message(message: WhatsAppMessage):
    # Save incoming user message
    intent = parse_intent(message.text)
    MessageService.save_message(message.store_id, message.sender, message.text, intent)
    
    # Process message and generate response
    bot_response = "I didn't understand that. You can try 'Bought 10 Rice bags' or 'Check stock'."
    
    if intent == "add_stock":
        bot_response = process_add_stock(message.store_id, message.text)
    elif intent == "check_stock":
        bot_response = process_check_stock(message.store_id, message.text)
    
    # Save bot response
    MessageService.save_message(message.store_id, "bot", bot_response, "system_reply")
    
    return {
        "reply": bot_response,
        "intent": intent
    }
    
@router.get("/history/{store_id}")
def get_chat_history(store_id: str):
    messages = MessageService.get_recent_messages(store_id, limit=50)
    # Sort by timestamp ascending for chat UI
    messages.sort(key=lambda x: x.get('timestamp', ''))
    return {"store_id": store_id, "messages": messages}

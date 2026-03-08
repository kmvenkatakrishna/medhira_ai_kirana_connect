"""
Amazon Bedrock Service for KiranaConnect AI.
Uses Claude 3 Haiku for intelligent, context-aware inventory assistance.
"""
import json
import boto3
from botocore.exceptions import ClientError

from backend.config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    BEDROCK_MODEL_ID, BEDROCK_ENABLED
)


class BedrockService:
    """Manages interactions with Amazon Bedrock for AI-powered chat."""

    def __init__(self):
        self.enabled = BEDROCK_ENABLED
        self.model_id = BEDROCK_MODEL_ID
        self.client = None

        if self.enabled and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            try:
                self.client = boto3.client(
                    "bedrock-runtime",
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )
                print(f"[OK] Bedrock connected: {self.model_id} in {AWS_REGION}")
            except Exception as e:
                print(f"[WARN] Bedrock init failed: {e}. Falling back to local AI.")
                self.client = None
        else:
            print("[INFO] Bedrock disabled or no credentials. Using local AI engine.")

    def is_available(self) -> bool:
        return self.client is not None

    def generate_response(
        self,
        user_message: str,
        inventory_context: str = "",
        ai_insights_context: str = "",
        conversation_history: list = None
    ) -> dict:
        """
        Generate an AI response using Amazon Bedrock Claude.

        Args:
            user_message: The store owner's message
            inventory_context: Current inventory data for context
            ai_insights_context: AI insights/predictions summary
            conversation_history: Recent messages for multi-turn

        Returns:
            dict with response text, confidence, and metadata
        """
        if not self.is_available():
            return None

        system_prompt = self._build_system_prompt(inventory_context, ai_insights_context)
        messages = self._build_messages(user_message, conversation_history)

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "temperature": 0.3,
                "system": system_prompt,
                "messages": messages
            })

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            ai_text = result["content"][0]["text"]

            return {
                "response": ai_text,
                "model": self.model_id,
                "powered_by": "Amazon Bedrock",
                "tokens_used": result.get("usage", {}).get("output_tokens", 0),
                "confidence": 0.92
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDeniedException":
                print(f"[WARN] Bedrock access denied. Ensure model {self.model_id} is enabled in {AWS_REGION}.")
            elif error_code == "ThrottlingException":
                print("[WARN] Bedrock rate limited. Using fallback.")
            else:
                print(f"[WARN] Bedrock error: {e}")
            return None

        except Exception as e:
            print(f"[WARN] Bedrock call failed: {e}")
            return None

    def _build_system_prompt(self, inventory_context: str, ai_insights_context: str) -> str:
        return f"""You are KiranaConnect AI, a smart inventory assistant for Indian Kirana (grocery) stores.
You help store owners manage inventory, predict demand, and make better business decisions.

IMPORTANT RULES:
- Respond in the SAME language the user writes in (Hindi, Hinglish, or English)
- Keep responses SHORT and actionable (under 150 words)
- Use emojis for better readability
- Always reference specific numbers and data when available
- Suggest next actions the store owner can take
- Use Indian Rupee (₹) for all currency values

CURRENT STORE DATA:
{inventory_context if inventory_context else "No inventory data loaded yet."}

AI INSIGHTS SUMMARY:
{ai_insights_context if ai_insights_context else "No insights available yet."}
"""

    def _build_messages(self, user_message: str, conversation_history: list = None) -> list:
        messages = []

        if conversation_history:
            for msg in conversation_history[-4:]:  # Keep last 4 messages for context
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    def generate_business_insight(self, data_summary: str) -> str:
        """Generate a natural language business insight from raw data."""
        if not self.is_available():
            return None

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.2,
                "system": "You are a business analytics AI for Indian Kirana stores. Generate 2-3 concise, actionable insights from the provided data. Use Hindi/English mix. Use emojis. Be specific with numbers.",
                "messages": [{
                    "role": "user",
                    "content": f"Analyze this store data and give actionable insights:\n{data_summary}"
                }]
            })

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            return result["content"][0]["text"]

        except Exception as e:
            print(f"[WARN] Bedrock insight generation failed: {e}")
            return None


# Singleton instance
bedrock_service = BedrockService()

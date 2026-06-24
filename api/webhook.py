#!/usr/bin/env python3
"""
NEXKEY — WhatsApp Webhook Handler
Vercel Serverless Function: api/webhook.py
"""

import json
import os
from datetime import datetime

# Vercel environment headers
def get_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


def verify_webhook(request):
    """Handle Meta's webhook verification challenge."""
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "nexkey_verify_token_2026")
    
    mode = request.get("query", {}).get("hub.mode", "")
    token = request.get("query", {}).get("hub.verify_token", "")
    challenge = request.get("query", {}).get("hub.challenge", "")
    
    if mode == "subscribe" and token == verify_token:
        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": str(challenge)
        }
    
    return {
        "statusCode": 403,
        "headers": get_headers(),
        "body": json.dumps({"error": "Verification failed"})
    }


def classify_lead(message_body):
    """Simple keyword-based lead classification."""
    hot_keywords = ["comprar", "buy", "presupuesto", "budget", "visita", "visit"]
    warm_keywords = ["info", "información", "information", "precio", "price"]
    
    message_lower = message_body.lower()
    
    if any(kw in message_lower for kw in hot_keywords):
        return "hot"
    elif any(kw in message_lower for kw in warm_keywords):
        return "warm"
    return "cold"


def process_incoming_message(message_data):
    """Process incoming WhatsApp message."""
    try:
        from_number = message_data.get("contacts", [{}])[0].get("wa_id", "")
        message_body = message_data.get("messages", [{}])[0].get("text", {}).get("body", "")
        
        # Classify lead
        lead_status = classify_lead(message_body)
        
        # Generate response
        responses = {
            "hot": "¡Gracias por tu interés! Un asesor te contactará pronto.",
            "warm": "¡Perfecto! Te envío más información sobre propiedades.",
            "cold": "Entendido. Te mantengo informado sobre nuevas propiedades."
        }
        
        response = responses.get(lead_status, "Gracias por escribirnos.")
        
        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": json.dumps({
                "status": "processed",
                "from": from_number,
                "lead_status": lead_status,
                "response": response
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": json.dumps({"status": "error", "error": str(e)})
        }


def handle_request(request):
    """Main webhook handler for Vercel."""
    # Handle CORS preflight
    if request.get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": ""
        }
    
    # Handle verification (GET request)
    if request.get("method") == "GET":
        return verify_webhook(request)
    
    # Handle incoming messages (POST request)
    if request.get("method") == "POST":
        try:
            body = json.loads(request.get("body", "{}"))
            
            # Meta sends messages in 'entry' array
            entries = body.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    if value.get("messages"):
                        for message in value["messages"]:
                            result = process_incoming_message(value)
                            return result
            
            return {
                "statusCode": 200,
                "headers": get_headers(),
                "body": json.dumps({"status": "received"})
            }
            
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": get_headers(),
                "body": json.dumps({"error": "Invalid JSON"})
            }
    
    return {
        "statusCode": 405,
        "headers": get_headers(),
        "body": json.dumps({"error": "Method not allowed"})
    }


# Vercel expects a 'handle' function
handle = handle_request

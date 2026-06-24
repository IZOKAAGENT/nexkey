#!/usr/bin/env python3
"""
NEXKEY — WhatsApp Webhook Handler
Receives incoming messages from Meta and routes them to agents.

Vercel Serverless Function: api/webhook.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Vercel environment headers
def get_headers():
    """Return CORS headers for Vercel"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

# Force redeploy marker: 2026-06-24-01


def verify_webhook(request):
    """
    Handle Meta's webhook verification challenge.
    GET request with hub.verify_token, hub.challenge, hub.mode
    """
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


def process_incoming_message(message_data):
    """
    Process incoming WhatsApp message and route to lead qualifier.
    """
    try:
        # Extract message info
        phone_number_id = message_data.get("metadata", {}).get("phone_number_id", "")
        from_number = message_data.get("contacts", [{}])[0].get("wa_id", "")
        message_body = message_data.get("messages", [{}])[0].get("text", {}).get("body", "")
        timestamp = message_data.get("messages", [{}])[0].get("timestamp", "")
        
        # Log the incoming message
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": from_number,
            "message": message_body,
            "phone_number_id": phone_number_id,
            "status": "received"
        }
        
        # Save to incoming messages log
        log_file = Path(__file__).parent.parent / "data" / "incoming_messages.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        messages = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []
        
        messages.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        # Route to lead qualifier agent
        response = route_to_lead_qualifier(from_number, message_body)
        
        return {
            "statusCode": 200,
            "headers": get_headers(),
            "body": json.dumps({
                "status": "processed",
                "from": from_number,
                "response_sent": response.get("sent", False)
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 200,  # Return 200 to acknowledge receipt even if processing fails
            "headers": get_headers(),
            "body": json.dumps({
                "status": "error",
                "error": str(e)
            })
        }


def route_to_lead_qualifier(from_number, message_body):
    """
    Route incoming message to lead qualifier agent.
    In production, this would call the agent via Hermes API.
    For now, we log it and prepare auto-response.
    """
    from scripts.auto_responder import AutoResponder
    
    responder = AutoResponder()
    
    # Determine lead status and generate response
    response = responder.process_incoming(from_number, message_body)
    
    # In live mode, this would send via WhatsApp
    # For now, we log the intended response
    return {"sent": True, "response": response}


def handle_request(request):
    """
    Main webhook handler for Vercel.
    """
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
                            # Return first result
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

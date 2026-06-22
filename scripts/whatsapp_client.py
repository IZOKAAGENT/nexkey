#!/usr/bin/env python3
"""
NEXKEY — WhatsApp Business API Integration
Handles sending messages via WhatsApp Business Cloud API.
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


class WhatsAppClient:
    """WhatsApp Business API client"""
    
    def __init__(self, phone_number_id, access_token, business_account_id=None):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.api_base = "https://graph.facebook.com/v18.0"
        
    def send_text_message(self, to, message, language="es"):
        """Send a text message via WhatsApp"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": "nexkey_lead_inquiry",
                "language": {
                    "code": language
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                ]
            }
        }
        
        return self._send_request(f"/{self.phone_number_id}/messages", payload)
    
    def send_template(self, to, template_name, parameters, language="es"):
        """Send a template message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": parameters
                    }
                ]
            }
        }
        
        return self._send_request(f"/{self.phone_number_id}/messages", payload)
    
    def _send_request(self, endpoint, payload):
        """Send HTTP request to WhatsApp API"""
        url = f"{self.api_base}{endpoint}"
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {self.access_token}')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    result = json.loads(response.read())
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": f"Status {response.status}"}
        except urllib.error.URLError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_connection(self):
        """Verify WhatsApp API connection"""
        endpoint = f"/{self.phone_number_id}"
        url = f"{self.api_base}{endpoint}"
        
        req = urllib.request.Request(url, method='GET')
        req.add_header('Authorization', f'Bearer {self.access_token}')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return {"connected": True, "data": json.loads(response.read())}
                else:
                    return {"connected": False, "error": f"Status {response.status}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}


def load_whatsapp_config():
    """Load WhatsApp configuration from settings"""
    config_path = Path(__file__).parent.parent / "config" / "whatsapp.yaml"
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None
    except ImportError:
        print("⚠️  PyYAML not installed")
        return None


def main():
    """Test WhatsApp connection"""
    print("=" * 50)
    print("NEXKEY — WhatsApp Business API Test")
    print("=" * 50)
    print()
    
    config = load_whatsapp_config()
    
    if not config:
        print("❌ WhatsApp configuration not found")
        print()
        print("📋 To configure WhatsApp:")
        print("   1. Register at: https://developers.facebook.com/docs/whatsapp/business-api")
        print("   2. Get your Phone Number ID and Access Token")
        print("   3. Create config/whatsapp.yaml")
        print()
        print("Example config/whatsapp.yaml:")
        print("""
whatsapp:
  phone_number_id: "YOUR_PHONE_NUMBER_ID"
  access_token: "YOUR_ACCESS_TOKEN"
  business_account_id: "YOUR_BUSINESS_ACCOUNT_ID"
  templates:
    - name: "nexkey_lead_inquiry"
      language: "es"
    - name: "nexkey_follow_up"
      language: "es"
""")
        return 1
    
    wa_config = config.get('whatsapp', {})
    phone_id = wa_config.get('phone_number_id')
    access_token = wa_config.get('access_token')
    
    if not phone_id or not access_token:
        print("❌ Missing WhatsApp credentials")
        print("   Check config/whatsapp.yaml")
        return 1
    
    client = WhatsAppClient(phone_id, access_token)
    result = client.verify_connection()
    
    if result.get('connected'):
        print("✅ WhatsApp API connected successfully!")
        print(f"   Phone Number ID: {phone_id[:10]}...")
        return 0
    else:
        print(f"❌ WhatsApp API connection failed: {result.get('error')}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

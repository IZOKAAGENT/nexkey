from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "nexkey_verify_token_2026")

def classify_lead(message_body):
    hot_keywords = ["comprar", "buy", "presupuesto", "budget", "visita", "visit"]
    warm_keywords = ["info", "información", "information", "precio", "price"]
    message_lower = message_body.lower()
    if any(kw in message_lower for kw in hot_keywords):
        return "hot"
    elif any(kw in message_lower for kw in warm_keywords):
        return "warm"
    return "cold"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verificación de Meta (GET)
    if request.method == "GET":
        if request.args.get("hub.mode") == "subscribe" and \
           request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge", ""), 200
        return "Forbidden", 403

    # Mensajes entrantes (POST)
    try:
        data = request.json
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if value.get("messages"):
                    for message in value["messages"]:
                        from_number = value.get("contacts", [{}])[0].get("wa_id", "")
                        message_body = message.get("text", {}).get("body", "")
                        lead_status = classify_lead(message_body)
                        
                        responses = {
                            "hot": "¡Gracias por tu interés! Un asesor te contactará pronto.",
                            "warm": "¡Perfecto! Te envío más información sobre propiedades.",
                            "cold": "Entendido. Te mantengo informado sobre nuevas propiedades."
                        }
                        
                        print(f"[NEXKEY] Lead {lead_status} from {from_number}: {message_body}")
                        return jsonify({
                            "status": "processed",
                            "lead_status": lead_status,
                            "response": responses.get(lead_status, "Gracias por escribirnos.")
                        }), 200
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

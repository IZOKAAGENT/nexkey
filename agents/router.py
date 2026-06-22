"""
NEXKEY — Intent Router Agent
Routes incoming messages to the correct agent based on intent + language.
"""

import yaml
from enum import Enum
from typing import Optional

class Language(Enum):
    ES = "es"
    EN = "en"

class Intent(Enum):
    LEAD_INBOUND = "lead_inbound"       # New lead coming in
    FOLLOW_UP = "follow_up"             # Existing prospect follow-up
    SCHEDULING = "scheduling"           # Appointment request
    PROSPECTING = "prospecting"         # Outbound prospecting
    UNKNOWN = "unknown"

class RouterAgent:
    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.lang_patterns = {
            Language.ES: ["hola", "buenos", "quiero", "necesito", "propiedad", "casa", "departamento", "precio", "visita"],
            Language.EN: ["hello", "hi", "want", "need", "property", "house", "apartment", "price", "visit", "looking"]
        }

    def detect_language(self, message: str) -> Language:
        """Detect if message is in Spanish or English."""
        msg_lower = message.lower()
        es_score = sum(1 for p in self.lang_patterns[Language.ES] if p in msg_lower)
        en_score = sum(1 for p in self.lang_patterns[Language.EN] if p in msg_lower)
        return Language.ES if es_score >= en_score else Language.EN

    def classify_intent(self, message: str, lang: Language) -> Intent:
        """Classify the intent of an incoming message."""
        msg_lower = message.lower()
        
        # Lead qualification keywords
        lead_keywords_es = ["quiero comprar", "quiero vender", "me interesa", "cuanto cuesta", "informacion"]
        lead_keywords_en = ["want to buy", "want to sell", "interested", "how much", "information", "tell me about"]
        
        # Follow-up keywords
        followup_keywords_es = ["seguimiento", "recordatorio", "volvi a preguntar", "actualizacion"]
        followup_keywords_en = ["follow up", "reminder", "checking back", "update"]
        
        # Scheduling keywords
        schedule_keywords_es = ["visita", "cita", "agendar", "cuando puedo", "disponible"]
        schedule_keywords_en = ["visit", "appointment", "schedule", "when can", "available", "tour"]
        
        keywords = lead_keywords_es if lang == Language.ES else lead_keywords_en
        if any(k in msg_lower for k in keywords):
            return Intent.LEAD_INBOUND
        
        keywords = followup_keywords_es if lang == Language.ES else followup_keywords_en
        if any(k in msg_lower for k in keywords):
            return Intent.FOLLOW_UP
        
        keywords = schedule_keywords_es if lang == Language.ES else schedule_keywords_en
        if any(k in msg_lower for k in keywords):
            return Intent.SCHEDULING
        
        return Intent.UNKNOWN

    def route(self, message: str) -> dict:
        """Route a message to the appropriate agent."""
        lang = self.detect_language(message)
        intent = self.classify_intent(message, lang)
        
        agent_map = {
            Intent.LEAD_INBOUND: "lead_qualifier",
            Intent.FOLLOW_UP: "follow_up",
            Intent.SCHEDULING: "scheduler",
            Intent.PROSPECTING: "prospector",
            Intent.UNKNOWN: "lead_qualifier"  # Default to qualifier
        }
        
        return {
            "language": lang.value,
            "intent": intent.value,
            "target_agent": agent_map[intent],
            "message": message
        }

    def get_template_path(self, intent: Intent, lang: Language) -> str:
        """Get the path to the appropriate response template."""
        template_map = {
            Intent.LEAD_INBOUND: "lead_qualification",
            Intent.FOLLOW_UP: "follow_up",
            Intent.SCHEDULING: "scheduling",
            Intent.UNKNOWN: "default_response"
        }
        return f"templates/{lang.value}/{template_map[intent]}.md"


if __name__ == "__main__":
    router = RouterAgent()
    
    # Test cases
    test_messages = [
        "Hola, quiero comprar un departamento en Madrid",
        "Hi, I'm looking for a house in Miami",
        "Cuándo puedo agendar una visita?",
        "I want to schedule a tour",
        "Necesito información sobre propiedades"
    ]
    
    for msg in test_messages:
        result = router.route(msg)
        print(f"Message: {msg[:40]}...")
        print(f"  → Language: {result['language']}, Intent: {result['intent']}, Agent: {result['target_agent']}")
        print()

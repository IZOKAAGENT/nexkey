"""
NEXKEY — Lead Qualifier Agent
Captures and qualifies inbound leads from WhatsApp, SMS, email.
Uses conversation flow to extract key info and score lead readiness.
"""

import yaml
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexkey.lead_qualifier")


@dataclass
class Lead:
    """Represents an inbound lead."""
    id: str
    name: str
    contact: str  # phone, email, or WhatsApp ID
    channel: str  # whatsapp, sms, email
    language: str  # es or en
    intent: str = ""  # buy, sell, rent, info
    budget: Optional[str] = None
    location: Optional[str] = None
    timeline: Optional[str] = None
    property_type: Optional[str] = None
    score: int = 0  # 0-100 qualification score
    status: str = "new"  # new, qualified, hot, cold, converted
    conversation_log: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class LeadScorer:
    """Scores leads based on qualification criteria."""

    def __init__(self):
        self.criteria = {
            "has_intent": 20,
            "has_budget": 20,
            "has_location": 15,
            "has_timeline": 15,
            "has_property_type": 15,
            "responsive": 15
        }

    def score(self, lead: Lead) -> int:
        """Score a lead from 0-100."""
        score = 0

        if lead.intent:
            score += self.criteria["has_intent"]
        if lead.budget:
            score += self.criteria["has_budget"]
        if lead.location:
            score += self.criteria["has_location"]
        if lead.timeline:
            score += self.criteria["has_timeline"]
        if lead.property_type:
            score += self.criteria["has_property_type"]

        # Responsive bonus (answered within first exchange)
        if len(lead.conversation_log) >= 2:
            score += self.criteria["responsive"]

        lead.score = min(score, 100)

        # Auto-classify status based on score
        if lead.score >= 80:
            lead.status = "hot"
        elif lead.score >= 50:
            lead.status = "qualified"
        elif lead.score >= 20:
            lead.status = "new"
        else:
            lead.status = "cold"

        return lead.score


class ConversationEngine:
    """Manages conversation flows for lead qualification."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.templates = self._load_templates()

    def _load_templates(self) -> dict:
        """Load conversation templates."""
        return {
            "es": {
                "greeting": "¡Hola [NOMBRE]! 👋 Soy el asistente virtual de [INMOBILIARIA]. ¿En qué puedo ayudarte?",
                "ask_intent": "¿Buscas comprar, vender o alquilar?",
                "ask_budget": "¿Cuál es tu presupuesto aproximado?",
                "ask_location": "¿En qué zona te gustaría buscar?",
                "ask_timeline": "¿Cuándo planeas hacer el movimiento?",
                "ask_property_type": "¿Qué tipo de propiedad te interesa? (casa, departamento, terreno, local comercial)",
                "qualified": "¡Perfecto! Ya tengo toda la información. Te conecto con un broker que te puede ayudar. ⏳",
                "cold": "Entiendo. Si cambias de opinión, estamos aquí cuando nos necesites. 😊"
            },
            "en": {
                "greeting": "Hi [NAME]! 👋 I'm the virtual assistant for [REALTY_COMPANY]. How can I help you?",
                "ask_intent": "Are you looking to buy, sell, or rent?",
                "ask_budget": "What's your approximate budget?",
                "ask_location": "Which area are you interested in?",
                "ask_timeline": "When are you planning to make the move?",
                "ask_property_type": "What type of property interests you? (house, apartment, land, commercial)",
                "qualified": "Perfect! I have all the info. Let me connect you with a broker who can help. ⏳",
                "cold": "I understand. If you change your mind, we're here when you need us. 😊"
            }
        }

    def get_next_question(self, lead: Lead) -> Optional[str]:
        """Determine the next question to ask based on what's missing."""
        lang = lead.language
        templates = self.templates[lang]

        if not lead.intent:
            return templates["ask_intent"]
        if not lead.budget:
            return templates["ask_budget"]
        if not lead.location:
            return templates["ask_location"]
        if not lead.timeline:
            return templates["ask_timeline"]
        if not lead.property_type:
            return templates["ask_property_type"]

        # All info collected
        return None

    def process_response(self, lead: Lead, response: str) -> dict:
        """Process a lead's response and extract information."""
        resp_lower = response.lower()
        extracted = {}

        # Extract intent
        if not lead.intent:
            if any(w in resp_lower for w in ["comprar", "buy", "purchase"]):
                lead.intent = "buy"
                extracted["intent"] = "buy"
            elif any(w in resp_lower for w in ["vender", "sell"]):
                lead.intent = "sell"
                extracted["intent"] = "sell"
            elif any(w in resp_lower for w in ["alquilar", "rent", "rental"]):
                lead.intent = "rent"
                extracted["intent"] = "rent"
            else:
                lead.intent = "info"
                extracted["intent"] = "info"

        # Extract budget (simple pattern matching)
        if not lead.budget:
            budget_keywords = ["$", "presupuesto", "budget", "precio", "price"]
            if any(kw in resp_lower for kw in budget_keywords):
                lead.budget = response[:50]  # Simplified
                extracted["budget"] = lead.budget

        # Extract location
        if not lead.location:
            location_keywords = ["en", "zona", "area", "location", "ciudad", "city", "barrio", "neighborhood"]
            if any(kw in resp_lower for kw in location_keywords):
                lead.location = response[:50]
                extracted["location"] = lead.location

        # Extract timeline
        if not lead.timeline:
            timeline_keywords = ["cuándo", "when", "pronto", "soon", "mes", "month", "semana", "week"]
            if any(kw in resp_lower for kw in timeline_keywords):
                lead.timeline = response[:50]
                extracted["timeline"] = lead.timeline

        # Extract property type
        if not lead.property_type:
            property_keywords = ["casa", "house", "departamento", "apartment", "terreno", "land", "local", "commercial"]
            if any(kw in resp_lower for kw in property_keywords):
                lead.property_type = response[:50]
                extracted["property_type"] = lead.property_type

        # Log the exchange
        lead.conversation_log.append({
            "type": "response",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "extracted": extracted
        })
        lead.last_updated = datetime.now().isoformat()

        return extracted


class LeadQualifierAgent:
    """Main lead qualification agent."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.scorer = LeadScorer()
        self.conversation = ConversationEngine(config_path)
        self.leads: list[Lead] = []
        self.mode = "dry-run"

    def create_lead(self, name: str, contact: str, channel: str, language: str) -> Lead:
        """Create a new lead entry."""
        lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        lead = Lead(
            id=lead_id,
            name=name,
            contact=contact,
            channel=channel,
            language=language
        )
        self.leads.append(lead)
        logger.info(f"New lead created: {lead_id} ({name})")
        return lead

    def process_inbound(self, lead: Lead, message: str) -> dict:
        """Process an inbound message from a lead."""
        # Process response
        extracted = self.conversation.process_response(lead, message)

        # Score the lead
        self.scorer.score(lead)

        # Get next question or determine if qualified
        next_question = self.conversation.get_next_question(lead)

        response = {
            "lead_id": lead.id,
            "status": lead.status,
            "score": lead.score,
            "extracted": extracted,
            "next_action": None,
            "response_message": None
        }

        if next_question:
            response["next_action"] = "ask_question"
            response["response_message"] = next_question
        elif lead.score >= 50:
            response["next_action"] = "connect_to_broker"
            lang = lead.language
            response["response_message"] = self.conversation.templates[lang]["qualified"]
            lead.status = "hot"
        else:
            response["next_action"] = "nurture"
            lang = lead.language
            response["response_message"] = self.conversation.templates[lang]["cold"]
            lead.status = "cold"

        return response

    def get_lead_summary(self, lead_id: str) -> Optional[dict]:
        """Get summary for a specific lead."""
        for lead in self.leads:
            if lead.id == lead_id:
                return {
                    "id": lead.id,
                    "name": lead.name,
                    "status": lead.status,
                    "score": lead.score,
                    "channel": lead.channel,
                    "language": lead.language,
                    "intent": lead.intent,
                    "budget": lead.budget,
                    "location": lead.location,
                    "timeline": lead.timeline,
                    "property_type": lead.property_type,
                    "conversation_count": len(lead.conversation_log),
                    "created_at": lead.created_at,
                    "last_updated": lead.last_updated
                }
        return None

    def get_pipeline_summary(self) -> dict:
        """Get summary of lead pipeline."""
        summary = {
            "total_leads": len(self.leads),
            "by_status": {},
            "by_channel": {},
            "by_language": {},
            "avg_score": 0,
            "hot_leads": [],
            "conversion_rate": 0
        }

        if not self.leads:
            return summary

        for lead in self.leads:
            summary["by_status"][lead.status] = summary["by_status"].get(lead.status, 0) + 1
            summary["by_channel"][lead.channel] = summary["by_channel"].get(lead.channel, 0) + 1
            summary["by_language"][lead.language] = summary["by_language"].get(lead.language, 0) + 1

        summary["avg_score"] = sum(l.score for l in self.leads) / len(self.leads)
        summary["hot_leads"] = [l.id for l in self.leads if l.status == "hot"]
        summary["conversion_rate"] = len(summary["hot_leads"]) / len(self.leads) * 100

        return summary


if __name__ == "__main__":
    agent = LeadQualifierAgent()

    print("=" * 60)
    print("NEXKEY LEAD QUALIFIER AGENT")
    print("=" * 60)

    # Create test leads
    lead1 = agent.create_lead("Carlos García", "+521234567890", "whatsapp", "es")
    lead2 = agent.create_lead("John Smith", "+12345678901", "sms", "en")

    # Simulate conversation
    print("\n📱 Simulating conversations...")

    # Lead 1: Spanish buyer
    messages_es = ["Quiero comprar una casa", "Mi presupuesto es $200K", "En CDMX", "En los próximos 2 meses", "Un departamento de 3 recámaras"]
    for msg in messages_es:
        result = agent.process_inbound(lead1, msg)
        print(f"   ES: '{msg[:30]}...' → Score: {result['score']}, Status: {result['status']}")

    # Lead 2: English renter
    messages_en = ["I want to rent an apartment", "Budget around $2K/month", "In Miami Beach", "Moving next month", "2 bedroom near beach"]
    for msg in messages_en:
        result = agent.process_inbound(lead2, msg)
        print(f"   EN: '{msg[:30]}...' → Score: {result['score']}, Status: {result['status']}")

    # Show pipeline summary
    summary = agent.get_pipeline_summary()
    print(f"\n📊 Pipeline Summary:")
    print(f"   Total leads: {summary['total_leads']}")
    print(f"   By status: {summary['by_status']}")
    print(f"   Avg score: {summary['avg_score']:.1f}")
    print(f"   Hot leads: {len(summary['hot_leads'])}")
    print(f"   Conversion rate: {summary['conversion_rate']:.1f}%")

    print("\n✅ Lead qualifier agent ready")

#!/usr/bin/env python3
"""
NEXKEY — Auto-Response System
Automatically responds to leads based on qualification status.
"""

import json
from datetime import datetime
from pathlib import Path


class AutoResponder:
    """Automated response generator for leads"""
    
    def __init__(self):
        self.response_templates = {
            "hot": {
                "es": "¡Gracias por tu interés! Un asesor te contactará en los próximos minutos para agendar una visita personalizada. ¿Qué tipo de propiedad buscas?",
                "en": "Thank you for your interest! An advisor will contact you in the next few minutes to schedule a personalized visit. What type of property are you looking for?"
            },
            "warm": {
                "es": "¡Perfecto! Te envío más información sobre propiedades disponibles. ¿Cuál es tu rango de presupuesto?",
                "en": "Perfect! I'll send you more information about available properties. What's your budget range?"
            },
            "cold": {
                "es": "Entendido. Te mantengo informado cuando tengamos nuevas propiedades que coincidan con tu búsqueda. ¿Prefieres actualizaciones por email o WhatsApp?",
                "en": "Understood. I'll keep you updated when we have new properties that match your search. Do you prefer updates via email or WhatsApp?"
            }
        }
    
    def generate_response(self, lead_data):
        """Generate appropriate response based on lead qualification"""
        score = lead_data.get("score", 0)
        language = lead_data.get("language", "es")
        
        if score >= 70:
            category = "hot"
        elif score >= 40:
            category = "warm"
        else:
            category = "cold"
        
        return {
            "category": category,
            "response": self.response_templates[category][language],
            "timestamp": datetime.now().isoformat(),
            "lead_id": lead_data.get("lead_id", "unknown")
        }
    
    def process_batch(self, leads):
        """Process multiple leads and generate responses"""
        responses = []
        for lead in leads:
            response = self.generate_response(lead)
            responses.append(response)
        return responses


def main():
    """Test auto-responder with sample leads"""
    print("=" * 50)
    print("NEXKEY — Auto-Response System Test")
    print("=" * 50)
    print()
    
    # Sample leads from previous campaigns
    sample_leads = [
        {
            "lead_id": "LEAD-001",
            "score": 85,
            "language": "es",
            "message": "Quiero comprar un departamento en Miami"
        },
        {
            "lead_id": "LEAD-002",
            "score": 65,
            "language": "en",
            "message": "Looking for a house in California"
        },
        {
            "lead_id": "LEAD-003",
            "score": 30,
            "language": "es",
            "message": "Solo estoy mirando opciones"
        }
    ]
    
    responder = AutoResponder()
    responses = responder.process_batch(sample_leads)
    
    for response in responses:
        print(f"Lead: {response['lead_id']}")
        print(f"Category: {response['category']}")
        print(f"Response: {response['response']}")
        print("-" * 40)
    
    print(f"\n✅ Generated {len(responses)} responses successfully")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

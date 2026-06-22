"""
NEXKEY — Prospector Agent (Dogfooding)
Self-prospecting agent that finds real estate companies and initiates outreach.
This IS the demo — we use our own product to sell our own product.
"""

import yaml
import json
import logging
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexkey.prospector")


@dataclass
class Prospect:
    """Represents a real estate company prospect."""
    name: str
    country: str
    language: str  # 'es' or 'en'
    website: Optional[str] = None
    platforms: list = field(default_factory=list)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    lead_score: int = 0  # 0-100 scoring
    status: str = "new"  # new, contacted, interested, meeting_booked, converted
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_contacted: Optional[str] = None


class ProspectScorer:
    """Scores prospects based on likelihood to convert."""

    def __init__(self):
        # Scoring criteria
        self.criteria = {
            "has_website": 15,
            "active_on_platforms": 20,
            "large_market": 15,
            "no_auto_response": 25,  # Biggest pain point
            "recent_listings": 15,
            "premium_segment": 10
        }

    def score(self, prospect: Prospect) -> int:
        """Score a prospect from 0-100."""
        score = 0

        # Has website = more established
        if prospect.website:
            score += self.criteria["has_website"]

        # Active on multiple platforms = more leads to capture
        platform_count = len(prospect.platforms)
        if platform_count >= 3:
            score += self.criteria["active_on_platforms"]
        elif platform_count >= 1:
            score += self.criteria["active_on_platforms"] // 2

        # Large markets = more budget
        large_markets = ["US", "MX", "ES", "AR", "CO", "CL", "PE"]
        if prospect.country in large_markets:
            score += self.criteria["large_market"]

        # No auto-response = biggest pain point (we assume most don't have it)
        score += self.criteria["no_auto_response"]

        # Recent activity indicator
        score += random.randint(0, self.criteria["recent_listings"])

        # Premium segment indicator
        if any(kw in prospect.name.lower() for kw in ["premium", "luxury", "exclusive", "elite"]):
            score += self.criteria["premium_segment"]

        prospect.lead_score = min(score, 100)
        return prospect.lead_score


class OutreachEngine:
    """Generates and tracks outreach campaigns."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.templates = self._load_templates()
        self.sent_messages = []

    def _load_templates(self) -> dict:
        """Load outreach templates from template files."""
        templates = {"es": [], "en": []}

        # Load from template files
        es_path = Path("templates/es/templates.md")
        en_path = Path("templates/en/templates.md")

        if es_path.exists():
            templates["es"].append(es_path.read_text())
        if en_path.exists():
            templates["en"].append(en_path.read_text())

        # Add built-in templates
        templates["es"].append(self._cold_outreach_es)
        templates["en"].append(self._cold_outreach_en)

        return templates

    @property
    def _cold_outreach_es(self) -> str:
        return """Hola [NOMBRE],

Te escribí a las 11pm a su anuncio en [PLATAFORMA] y nadie respondió. 😅

Imagino cuántos leads pierden sus brokers por no responder a tiempo.

En NEXKEY instalamos un agente de IA que:
✅ Responde en <3 segundos, 24/7
✅ Califica leads automáticamente
✅ Agendas visitas sin intervención humana

Última semana, un cliente nuestro recuperó 47 leads "perdidos" y generó $23K en comisiones.

¿Te hace sentido una llamada de 10 min para mostrarle cómo funciona?"""

    @property
    def _cold_outreach_en(self) -> str:
        return """Hi [NAME],

I messaged your listing on [PLATFORM] at 11pm and got no response. 😅

I can imagine how many leads your brokers lose from not responding fast enough.

At NEXKEY, we install an AI agent that:
✅ Responds in <3 seconds, 24/7
✅ Auto-qualifies leads
✅ Schedules viewings with zero human intervention

Last week, one of our clients recovered 47 "lost" leads and generated $23K in commissions.

Does a quick 10-min call to show you how it works make sense?"""

    def generate_message(self, prospect: Prospect) -> str:
        """Generate a personalized outreach message."""
        lang = prospect.language
        template = self.templates[lang][-1]  # Use latest template

        # Personalize
        message = template.replace("[NOMBRE]", prospect.name)
        message = message.replace("[NAME]", prospect.name)
        message = message.replace("[PLATAFORMA]", prospect.platforms[0] if prospect.platforms else "varias plataformas")
        message = message.replace("[PLATFORM]", prospect.platforms[0] if prospect.platforms else "various platforms")

        return message

    def send(self, prospect: Prospect, message: str, channel: str = "email") -> bool:
        """Simulate sending a message (dry-run mode)."""
        # In production, this would integrate with WhatsApp Business API, Twilio, etc.
        record = {
            "prospect_name": prospect.name,
            "channel": channel,
            "timestamp": datetime.now().isoformat(),
            "message_preview": message[:100] + "...",
            "status": "sent"
        }
        self.sent_messages.append(record)
        prospect.last_contacted = datetime.now().isoformat()
        prospect.status = "contacted"
        logger.info(f"Outreach sent to {prospect.name} via {channel}")
        return True


class ProspectorAgent:
    """Main prospector agent — finds and contacts real estate companies."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.scorer = ProspectScorer()
        self.outreach = OutreachEngine(config_path)
        self.prospects: list[Prospect] = []
        self.mode = "dry-run"

        # Seed with sample prospects for demo
        self._seed_prospects()

    def _seed_prospects(self):
        """Seed with sample prospects for demonstration."""
        sample_prospects = [
            # Spanish market (LatAm)
            Prospect("Inmobiliaria Premium MX", "MX", "es", "premiummx.com", ["Facebook", "MercadoLibre", "VipProperties"], "contacto@premiummx.com"),
            Prospect("Elite Properties Colombia", "CO", "es", "eliteproperties.co", ["Facebook", "FincaRaíz"], "info@eliteproperties.co"),
            Prospect("Bienes Raíces del Sur", "AR", "es", "brsur.com.ar", ["Facebook", "AmbitoInmobiliario", "Zonaprop"], "ventas@brsur.com.ar"),
            Prospect("Luxury Homes Chile", "CL", "es", "luxuryhomes.cl", ["Facebook", "YapoImobiliario"], "contacto@luxuryhomes.cl"),
            Prospect("Inmobiliaria Lima Plus", "PE", "es", "limaplus.pe", ["Facebook", "UbiHouse"], "info@limaplus.pe"),

            # English market (US)
            Prospect("Miami Luxury Realty", "US", "en", "miamiluxury.com", ["Zillow", "Realtor.com", "Facebook"], "info@miamiluxury.com"),
            Prospect("Sunshine Properties FL", "US", "en", "sunshineproperties.com", ["Zillow", "Trulia"], "contact@sunshineproperties.com"),
            Prospect("Elite Estates California", "US", "en", "eliteestates.com", ["Zillow", "Realtor.com", "Redfin"], "sales@eliteestates.com"),
            Prospect("Texas Premier Realty", "US", "en", "texaspremier.com", ["Zillow", "Facebook"], "info@texaspremier.com"),
            Prospect("NYC Premium Properties", "US", "en", "nycpremium.com", ["StreetEasy", "Zillow", "Realtor.com"], "contact@nycpremium.com"),
        ]

        for prospect in sample_prospects:
            self.scorer.score(prospect)
            self.prospects.append(prospect)

    def get_top_prospects(self, count: int = 5, min_score: int = 50) -> list[Prospect]:
        """Get top-scoring prospects."""
        filtered = [p for p in self.prospects if p.lead_score >= min_score and p.status == "new"]
        sorted_prospects = sorted(filtered, key=lambda p: p.lead_score, reverse=True)
        return sorted_prospects[:count]

    def run_campaign(self, prospect_count: int = 5, min_score: int = 50) -> dict:
        """Run a prospecting campaign."""
        logger.info(f"Starting prospecting campaign: {prospect_count} prospects, min_score={min_score}")

        targets = self.get_top_prospects(prospect_count, min_score)
        results = {
            "campaign_id": f"CAMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "targets": [],
            "sent": 0,
            "failed": 0
        }

        for prospect in targets:
            try:
                message = self.outreach.generate_message(prospect)
                success = self.outreach.send(prospect, message)

                results["targets"].append({
                    "name": prospect.name,
                    "country": prospect.country,
                    "score": prospect.lead_score,
                    "status": "sent" if success else "failed"
                })

                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1

                # Simulate delay between messages
                if self.mode != "dry-run":
                    time.sleep(random.uniform(1, 3))

            except Exception as e:
                logger.error(f"Failed to contact {prospect.name}: {e}")
                results["failed"] += 1

        logger.info(f"Campaign complete: {results['sent']} sent, {results['failed']} failed")
        return results

    def get_pipeline_summary(self) -> dict:
        """Get summary of prospecting pipeline."""
        summary = {
            "total_prospects": len(self.prospects),
            "by_status": {},
            "by_country": {},
            "avg_score": 0,
            "top_scored": []
        }

        # Count by status
        for prospect in self.prospects:
            summary["by_status"][prospect.status] = summary["by_status"].get(prospect.status, 0) + 1
            summary["by_country"][prospect.country] = summary["by_country"].get(prospect.country, 0) + 1

        # Average score
        if self.prospects:
            summary["avg_score"] = sum(p.lead_score for p in self.prospects) / len(self.prospects)

        # Top 5 scored
        summary["top_scored"] = [
            {"name": p.name, "score": p.lead_score, "status": p.status}
            for p in sorted(self.prospects, key=lambda x: x.lead_score, reverse=True)[:5]
        ]

        return summary

    def add_prospect(self, prospect_data: dict) -> Prospect:
        """Add a new prospect to the pipeline."""
        prospect = Prospect(**prospect_data)
        self.scorer.score(prospect)
        self.prospects.append(prospect)
        logger.info(f"New prospect added: {prospect.name} (score: {prospect.lead_score})")
        return prospect


if __name__ == "__main__":
    agent = ProspectorAgent()

    print("=" * 60)
    print("NEXKEY PROSPECTOR AGENT — Dogfooding Mode")
    print("=" * 60)

    # Show pipeline summary
    summary = agent.get_pipeline_summary()
    print(f"\n📊 Pipeline Summary:")
    print(f"   Total prospects: {summary['total_prospects']}")
    print(f"   Average score: {summary['avg_score']:.1f}")
    print(f"   By status: {summary['by_status']}")
    print(f"   By country: {summary['by_country']}")

    # Show top prospects
    print(f"\n🎯 Top 5 Prospects:")
    for i, p in enumerate(summary['top_scored'], 1):
        print(f"   {i}. {p['name']} — Score: {p['score']} ({p['status']})")

    # Run campaign
    print(f"\n🚀 Running outreach campaign...")
    results = agent.run_campaign(prospect_count=5, min_score=50)
    print(f"   Campaign: {results['campaign_id']}")
    print(f"   Sent: {results['sent']}, Failed: {results['failed']}")

    print("\n✅ Prospector agent ready")

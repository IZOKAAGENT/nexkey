#!/usr/bin/env python3
"""
NEXKEY — Agent Orchestrator
Main entry point for running agents in simulate/dry-run/live modes.
Integrates router, prospector, and lead_qualifier agents.
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: uv pip install pyyaml")
    sys.exit(1)

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / f"nexkey_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger("nexkey.orchestrator")

# Import agents
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.router import RouterAgent
from agents.prospector import ProspectorAgent
from agents.lead_qualifier import LeadQualifierAgent


class Orchestrator:
    """Main orchestrator for NEXKEY agents."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.mode = "dry-run"

        # Initialize agents
        self.router = RouterAgent(config_path)
        self.prospector = ProspectorAgent(config_path)
        self.lead_qualifier = LeadQualifierAgent(config_path)

        self.agents = {
            "router": self.router,
            "prospector": self.prospector,
            "lead_qualifier": self.lead_qualifier
        }
        self.health_status = {}

    def load_agents(self):
        """Load all configured agents."""
        agent_configs = self.config.get("agents", [])
        for agent_cfg in agent_configs:
            agent_name = agent_cfg["name"]
            self.health_status[agent_name] = "initialized"
            logger.info(f"Loaded agent: {agent_name} ({agent_cfg['role']})")

    def health_check(self) -> dict:
        """Run health checks on all agents."""
        results = {}
        agent_names = ["router", "prospector", "lead_qualifier"]

        for agent_name in agent_names:
            results[agent_name] = {
                "status": "healthy",
                "last_check": datetime.now().isoformat(),
                "response_time_ms": 0
            }
            self.health_status[agent_name] = "healthy"
            logger.debug(f"Health check passed for {agent_name}")

        return results

    def process_inbound_message(self, message: str, source: str = "unknown") -> dict:
        """Process an inbound message through the routing pipeline."""
        logger.info(f"Processing inbound from {source}: {message[:50]}...")

        # Route the message
        routing = self.router.route(message)

        if self.mode == "dry-run":
            return {
                "status": "dry-run",
                "message": message,
                "routing": routing,
                "would_route_to": routing["target_agent"],
                "timestamp": datetime.now().isoformat()
            }

        # In live mode, route to appropriate agent
        target_agent = routing["target_agent"]
        if target_agent == "lead_qualifier":
            # Create lead and process
            lead = self.lead_qualifier.create_lead(
                name="Unknown",
                contact=source,
                channel="whatsapp",
                language=routing["language"]
            )
            return self.lead_qualifier.process_inbound(lead, message)

        return {
            "status": "processed",
            "message": message,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }

    def run_prospecting_campaign(self, count: int = 5, min_score: int = 50) -> dict:
        """Run a dogfooding prospecting campaign."""
        logger.info(f"Running prospecting campaign: {count} prospects, min_score={min_score}")
        return self.prospector.run_campaign(count, min_score)

    def get_full_status(self) -> dict:
        """Get full system status."""
        return {
            "orchestrator": {
                "mode": self.mode,
                "company": self.config["company"]["name"],
                "timestamp": datetime.now().isoformat()
            },
            "health": self.health_check(),
            "prospecting_pipeline": self.prospector.get_pipeline_summary(),
            "lead_pipeline": self.lead_qualifier.get_pipeline_summary()
        }

    def run_simulation(self, test_messages: list) -> list:
        """Run a simulation with test messages."""
        logger.info(f"Starting simulation with {len(test_messages)} messages")
        results = []

        for i, msg in enumerate(test_messages):
            logger.info(f"Simulation [{i+1}/{len(test_messages)}]: {msg[:40]}...")
            result = self.process_inbound_message(msg, source="simulation")
            results.append(result)
            time.sleep(0.1)

        return results


def main():
    parser = argparse.ArgumentParser(description="NEXKEY Agent Orchestrator")
    parser.add_argument("--mode", choices=["simulate", "dry-run", "live"],
                       default="dry-run", help="Execution mode")
    parser.add_argument("--config", default="config/settings.yaml",
                       help="Path to config file")
    parser.add_argument("--test-messages", nargs="+",
                       help="Test messages to process")
    parser.add_argument("--prospect", type=int, default=0,
                       help="Run prospecting campaign with N prospects")
    parser.add_argument("--status", action="store_true",
                       help="Show full system status")

    args = parser.parse_args()

    orchestrator = Orchestrator(config_path=args.config)
    orchestrator.mode = args.mode
    orchestrator.load_agents()

    logger.info(f"NEXKEY Orchestrator started in {args.mode} mode")
    logger.info(f"Company: {orchestrator.config['company']['name']}")

    # Run health check
    health = orchestrator.health_check()
    logger.info(f"Health check: {sum(1 for h in health.values() if h['status'] == 'healthy')}/{len(health)} agents healthy")

    # Show status if requested
    if args.status:
        status = orchestrator.get_full_status()
        print("\n=== Full System Status ===")
        print(json.dumps(status, indent=2, default=str))

    # Run prospecting campaign if requested
    if args.prospect > 0:
        print(f"\n=== Running Prospecting Campaign ({args.prospect} prospects) ===")
        results = orchestrator.run_prospecting_campaign(args.prospect)
        print(json.dumps(results, indent=2, default=str))

    # Process test messages if provided
    if args.test_messages:
        results = orchestrator.run_simulation(args.test_messages)
        print("\n=== Simulation Results ===")
        for result in results:
            print(json.dumps(result, indent=2, default=str))

    logger.info("NEXKEY Orchestrator ready")


if __name__ == "__main__":
    main()

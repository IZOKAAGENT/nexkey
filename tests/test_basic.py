"""
NEXKEY — Test Suite
Basic tests for agents and orchestration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.router import RouterAgent, Language, Intent

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from orchestrate import Orchestrator

class TestRouter:
    """Test the router agent."""
    
    def setup_method(self):
        self.router = RouterAgent()
    
    def test_detect_language_spanish(self):
        """Test Spanish language detection."""
        result = self.router.detect_language("Hola, quiero comprar una casa")
        assert result == Language.ES
    
    def test_detect_language_english(self):
        """Test English language detection."""
        result = self.router.detect_language("Hi, I want to buy a house")
        assert result == Language.EN
    
    def test_classify_lead_intent(self):
        """Test lead qualification intent classification."""
        intent = self.router.classify_intent("Quiero comprar un departamento", Language.ES)
        assert intent == Intent.LEAD_INBOUND
    
    def test_route_message(self):
        """Test message routing."""
        result = self.router.route("Hello, I'm interested in properties")
        assert result["language"] == "en"
        assert result["intent"] == "lead_inbound"
        assert result["target_agent"] == "lead_qualifier"

class TestOrchestrator:
    """Test the orchestrator."""
    
    def setup_method(self):
        self.orchestrator = Orchestrator()
        self.orchestrator.load_agents()
    
    def test_agents_loaded(self):
        """Test that agents are loaded."""
        assert len(self.orchestrator.agents) > 0
    
    def test_health_check(self):
        """Test health check functionality."""
        health = self.orchestrator.health_check()
        assert len(health) > 0
        assert all(h["status"] == "healthy" for h in health.values())
    
    def test_process_message(self):
        """Test message processing."""
        result = self.orchestrator.process_message("Test message")
        assert result["status"] == "dry-run"
        assert "timestamp" in result

if __name__ == "__main__":
    # Run tests manually
    print("Running NEXKEY test suite...")
    
    # Test Router
    router_tests = TestRouter()
    router_tests.setup_method()
    
    print("Testing language detection...")
    router_tests.test_detect_language_spanish()
    router_tests.test_detect_language_english()
    print("✓ Language detection works")
    
    print("Testing intent classification...")
    router_tests.test_classify_lead_intent()
    print("✓ Intent classification works")
    
    print("Testing message routing...")
    router_tests.test_route_message()
    print("✓ Message routing works")
    
    # Test Orchestrator
    orch_tests = TestOrchestrator()
    orch_tests.setup_method()
    
    print("Testing orchestrator...")
    orch_tests.test_agents_loaded()
    orch_tests.test_health_check()
    orch_tests.test_process_message()
    print("✓ Orchestrator works")
    
    print("\n🎉 All tests passed!")

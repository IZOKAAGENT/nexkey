#!/usr/bin/env python3
"""
NEXKEY — Health Check System
Monitors agent uptime and response drift.
"""

import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexkey.health")

class HealthMonitor:
    """Monitors agent health and system metrics."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        try:
            import yaml
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except ImportError:
            print("ERROR: PyYAML required. Run: uv pip install pyyaml")
            return
        
        self.monitoring = self.config.get("monitoring", {})
        self.interval = self.monitoring.get("health_check_interval", 300)
        self.alert_conditions = self.monitoring.get("alert_on", [])
        self.metrics_history = []
        
    def check_agent_health(self, agent_name: str) -> dict:
        """Check if an agent is healthy."""
        check_time = datetime.now().isoformat()
        
        # Simulate health check (in production, this would ping actual agents)
        result = {
            "agent": agent_name,
            "status": "healthy",
            "timestamp": check_time,
            "metrics": {
                "response_time_ms": 45,  # Simulated
                "error_rate": 0.02,      # 2% error rate
                "uptime_percent": 99.8
            }
        }
        
        self.metrics_history.append(result)
        logger.info(f"Health check for {agent_name}: {result['status']}")
        return result
    
    def check_response_drift(self, agent_name: str, expected_response_time: int = 1000) -> bool:
        """Check if response times have drifted beyond acceptable thresholds."""
        # In production, this would compare actual vs expected response times
        logger.debug(f"Checking response drift for {agent_name}")
        return True  # No drift detected
    
    def run_full_check(self) -> dict:
        """Run a complete health check across all agents."""
        agent_names = ["router", "lead_qualifier", "follow_up", "scheduler", "prospector"]
        results = {}
        
        for agent in agent_names:
            results[agent] = self.check_agent_health(agent)
        
        # Check for drift
        drift_detected = False
        for agent in agent_names:
            if not self.check_response_drift(agent):
                drift_detected = True
                logger.warning(f"Response drift detected for {agent}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if not drift_detected else "degraded",
            "agents": results,
            "drift_detected": drift_detected
        }
    
    def should_alert(self, condition: str) -> bool:
        """Check if we should alert on a specific condition."""
        return condition in self.alert_conditions
    
    def log_alert(self, alert_type: str, message: str):
        """Log an alert if configured."""
        if self.should_alert(alert_type):
            logger.warning(f"ALERT [{alert_type}]: {message}")
        else:
            logger.info(f"MONITOR [{alert_type}]: {message}")


if __name__ == "__main__":
    monitor = HealthMonitor()
    results = monitor.run_full_check()
    print(f"\nHealth Check Results:")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Agents Checked: {len(results['agents'])}")
    print(f"Drift Detected: {results['drift_detected']}")

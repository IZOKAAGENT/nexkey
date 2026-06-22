#!/usr/bin/env python3
"""
NEXKEY — Circuit Breaker Pattern
Prevents cascade failures by tripping when agents fail repeatedly.
"""

import time
import logging
from enum import Enum
from datetime import datetime
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexkey.circuit_breaker")

class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """
    Circuit breaker implementation for NEXKEY agents.
    
    States:
    - CLOSED: Normal operation, requests flow through
    - OPEN: Agent is failing, requests are rejected
    - HALF_OPEN: Testing if agent has recovered
    """
    
    def __init__(self, name: str, failure_threshold: int = 3, 
                 recovery_timeout: int = 600, half_open_max_calls: int = 1):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        
    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time > self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker [{self.name}] transitioning to HALF_OPEN")
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
            
        return False
    
    def record_success(self):
        """Record a successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 1:  # One success in half-open is enough
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker [{self.name}] recovered - CLOSED")
        else:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open goes back to open
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker [{self.name}] failed in HALF_OPEN - OPEN")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker [{self.name}] tripped after {self.failure_count} failures - OPEN")
    
    def get_state(self) -> dict:
        """Get current circuit breaker state."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "threshold": self.failure_threshold
        }

class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> any:
        """Execute a function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Retry succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_exception


if __name__ == "__main__":
    # Test circuit breaker
    cb = CircuitBreaker("test_agent", failure_threshold=3, recovery_timeout=5)
    
    print("Initial state:", cb.get_state())
    
    # Simulate some failures
    for i in range(3):
        cb.record_failure()
        print(f"After failure {i+1}:", cb.get_state())
    
    # Wait for recovery timeout
    print("\nWaiting for recovery timeout...")
    time.sleep(6)
    
    # Try to execute (should transition to half-open)
    if cb.can_execute():
        print("Circuit breaker allowed execution (HALF_OPEN)")
        cb.record_success()
        print("After success:", cb.get_state())

"""
Base connector classes with retry, timeout, and cost tracking.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
from dataclasses import dataclass
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class ProviderCallResult:
    """Standardized result for provider API calls"""
    ok: bool
    data: Any = None
    cost_estimate: float = 0.0
    message: Optional[str] = None
    latency_ms: int = 0

def _now_ms(): 
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)

class BaseLLM:
    """Base class for LLM providers with retry and error handling"""
    model_name: str

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2))
    def complete(self, prompt: str, **kwargs) -> ProviderCallResult:
        """Complete a prompt with retry logic"""
        raise NotImplementedError("Must implement complete method")
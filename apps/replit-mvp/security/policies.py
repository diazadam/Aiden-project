"""
Security policies for capability-based permissions and PIN gating.
"""
import os
from typing import Iterable

# Master PIN for elevated capabilities (set in .env.local)
SECRET_PIN = os.environ.get("AIDEN_MASTER_PIN", "0000")  

class CapsPolicy:
    """Capability-based security policy enforcement"""
    
    # Capabilities that require PIN authentication
    DANGEROUS = {"fs_write", "exec", "net", "system"}

    @classmethod
    def requires_pin(cls, caps: Iterable[str]) -> bool:
        """Check if any capability requires PIN authentication"""
        return any(cap in cls.DANGEROUS for cap in caps)
    
    @classmethod
    def is_safe(cls, caps: Iterable[str]) -> bool:
        """Check if all capabilities are considered safe (no PIN needed)"""
        return not cls.requires_pin(caps)
    
    @classmethod
    def validate_pin(cls, provided_pin: str) -> bool:
        """Validate a provided PIN against the master PIN"""
        return provided_pin == SECRET_PIN
"""
Skills contract definitions and base classes for the self-expanding skills system.
"""
from __future__ import annotations
from typing import Any, Dict, Set, Optional, Type
from pydantic import BaseModel, Field

# Capabilities that may require PIN or elevated approval
DANGEROUS_CAPS = {"fs_write", "exec", "net", "system"}

class SkillInputs(BaseModel):
    """Base class for skill input parameters"""
    pass

class SkillOutputs(BaseModel):
    """Base class for skill output results"""
    ok: bool = Field(default=True, description="Did the skill succeed?")
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, str]] = None  # e.g., file paths, urls

class SkillContext(BaseModel):
    """Runtime context provided to skills during execution"""
    account_id: str
    workdir: str           # tenant-scoped working directory
    trace_id: str
    caps_token: Optional[str] = None  # runtime-provided token granting caps

class Skill:
    """Base skill class that all skills must inherit from"""
    name: str = "base"
    version: str = "0.0.1"
    caps: Set[str] = set()    # e.g. {"fs_write"}

    # Pydantic models for I/O
    Inputs: Type[SkillInputs] = SkillInputs
    Outputs: Type[SkillOutputs] = SkillOutputs

    def run(self, ctx: SkillContext, args: SkillInputs) -> SkillOutputs:
        """Execute the skill with given context and arguments"""
        raise NotImplementedError("Skill must implement run()")
"""
🎯 AIDEN SKILLS SYSTEM V1 - Self-Expanding Capabilities

Dynamic skill discovery, validation, and execution with sandboxed runtime.
Enables Aiden to learn new skills on the fly with governance and safety rails.
"""

from .registry import REGISTRY
from .contracts import Skill, SkillInputs, SkillOutputs, SkillContext
from .runtime import run_skill

__all__ = ["REGISTRY", "Skill", "SkillInputs", "SkillOutputs", "SkillContext", "run_skill"]
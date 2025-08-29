"""
Skills registry for dynamic skill discovery, loading, and management.
"""
from __future__ import annotations
import importlib.util
import json
import os
import sys
import hashlib
import types
from dataclasses import dataclass
from typing import Dict, Optional, List
from pydantic import BaseModel
from .contracts import Skill, DANGEROUS_CAPS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_SYSTEM_DIR = os.path.join(os.path.dirname(__file__), "_system")
SKILLS_STORE_DIR  = os.path.join(os.path.dirname(__file__), "..", "skills_store")
APPROVED_DIR      = os.path.join(SKILLS_STORE_DIR, "approved")
PENDING_DIR       = os.path.join(SKILLS_STORE_DIR, "pending")
AUDIT_LOG         = os.path.join(SKILLS_STORE_DIR, "audit.log")

# Ensure directories exist
os.makedirs(SKILLS_SYSTEM_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)

class Manifest(BaseModel):
    """Skill manifest metadata"""
    name: str
    version: str
    caps: List[str] = []
    description: str = ""
    checksum: Optional[str] = None   # sha256 of code

@dataclass
class RegisteredSkill:
    """Container for a loaded skill with its metadata"""
    module: types.ModuleType
    instance: Skill
    manifest: Manifest
    path: str
    enabled: bool = True

class SkillsRegistry:
    """Central registry for all loaded skills"""
    
    def __init__(self):
        self._by_name: Dict[str, RegisteredSkill] = {}

    def list(self) -> List[Dict]:
        """List all registered skills with metadata"""
        out = []
        for name, rs in sorted(self._by_name.items()):
            out.append({
                "name": name,
                "version": rs.manifest.version,
                "caps": rs.manifest.caps,
                "enabled": rs.enabled,
                "path": rs.path,
                "description": rs.manifest.description
            })
        return out

    def load_all(self):
        """Load all skills from system and approved directories"""
        # Clear existing registry
        self._by_name.clear()
        
        # Load system skills
        self._load_dir(SKILLS_SYSTEM_DIR, system=True)
        
        # Load approved store skills
        self._load_dir(APPROVED_DIR, system=False)

    def _load_dir(self, base_dir: str, system: bool):
        """Load skills from a directory"""
        if not os.path.exists(base_dir):
            return
            
        for entry in os.listdir(base_dir):
            path = os.path.join(base_dir, entry)
            if not os.path.isdir(path):
                continue
                
            manifest_path = os.path.join(path, "manifest.json")
            code_path = os.path.join(path, "skill.py")
            
            if not (os.path.exists(manifest_path) and os.path.exists(code_path)):
                continue
                
            try:
                # Load manifest
                with open(manifest_path, "r") as f:
                    manifest = Manifest.model_validate_json(f.read())
                
                # Optional checksum verification
                if manifest.checksum:
                    with open(code_path, "rb") as cf:
                        h = hashlib.sha256(cf.read()).hexdigest()
                        if h != manifest.checksum:
                            print(f"[skills] checksum mismatch for {entry}, skipping")
                            continue
                
                # Load the module
                mod_name = f"aiden_skill_{entry}_{'sys' if system else 'user'}"
                spec = importlib.util.spec_from_file_location(mod_name, code_path)
                if not spec or not spec.loader:
                    print(f"[skills] failed to load spec for {entry}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)
                
                if not hasattr(module, "SkillImpl"):
                    print(f"[skills] {entry} missing SkillImpl class")
                    continue
                    
                impl = module.SkillImpl()
                
                if impl.name in self._by_name:
                    print(f"[skills] duplicate skill name {impl.name}, skipping")
                    continue
                    
                self._by_name[impl.name] = RegisteredSkill(
                    module=module,
                    instance=impl,
                    manifest=manifest,
                    path=path,
                    enabled=True
                )
                
                print(f"[skills] loaded {impl.name} v{impl.version} caps={impl.caps}")
                
            except Exception as e:
                print(f"[skills] failed to load {entry}: {e}")
                continue

    def get(self, name: str) -> Optional[RegisteredSkill]:
        """Get a registered skill by name"""
        return self._by_name.get(name)

    def enable(self, name: str, enabled: bool = True) -> bool:
        """Enable or disable a skill"""
        rs = self._by_name.get(name)
        if not rs:
            return False
        rs.enabled = enabled
        return True

    def requires_pin(self, name: str) -> bool:
        """Check if a skill requires PIN for execution"""
        rs = self._by_name.get(name)
        if not rs:
            return False
        return any(c in DANGEROUS_CAPS for c in rs.manifest.caps)

# Global registry instance
REGISTRY = SkillsRegistry()
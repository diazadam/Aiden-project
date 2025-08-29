"""
AidenAI Supabase Memory System - Smart memory with vector search and pattern learning
"""
from __future__ import annotations
import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class MemoryEntry:
    id: Optional[str] = None
    timestamp: Optional[float] = None
    query: str = ""
    response: str = ""
    skill_used: str = ""
    account_id: str = "local"
    success: bool = True
    cost_usd: float = 0.0
    artifacts: Dict[str, Any] = None
    embedding: Optional[List[float]] = None

class SupabaseMemory:
    """Enhanced memory system using Supabase with vector search capabilities"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.openai_client = None
        self.table_name = "aiden_memory"
        
        # Initialize Supabase if available
        if SUPABASE_AVAILABLE:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_SERVICE_KEY")
            if url and key:
                try:
                    self.client = create_client(url, key)
                    self._ensure_table()
                except Exception as e:
                    print(f"Warning: Supabase initialization failed: {e}")
        
        # Initialize OpenAI for embeddings if available
        if OPENAI_AVAILABLE:
            try:
                self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except Exception as e:
                print(f"Warning: OpenAI initialization failed: {e}")
    
    def _ensure_table(self):
        """Ensure the memory table exists with proper schema"""
        if not self.client:
            return
            
        # Note: In production, you should create this table manually or via migration
        # This is a simplified check
        try:
            # Test if table exists by trying to select from it
            result = self.client.table(self.table_name).select("id").limit(1).execute()
        except Exception:
            print(f"Warning: Table {self.table_name} may not exist. Please create it manually.")
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using OpenAI"""
        if not self.openai_client:
            return None
            
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text[:8000]  # Limit text length
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Warning: Embedding generation failed: {e}")
            return None
    
    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store a memory entry with optional embedding"""
        if not self.client:
            return self._store_local_fallback(entry)
        
        try:
            # Generate embedding if possible
            if entry.query and self.openai_client:
                entry.embedding = self._get_embedding(entry.query)
            
            # Set timestamp if not provided
            if not entry.timestamp:
                entry.timestamp = time.time()
            
            # Convert to dict for storage
            data = asdict(entry)
            if data.get("artifacts") is None:
                data["artifacts"] = {}
            
            # Store in Supabase
            result = self.client.table(self.table_name).insert(data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Warning: Memory storage failed: {e}")
            return self._store_local_fallback(entry)
    
    def find_similar_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Find similar memories using vector search or text matching"""
        if not self.client:
            return self._find_local_fallback(query, limit)
        
        try:
            # If we have embeddings capability, use vector search
            if self.openai_client:
                query_embedding = self._get_embedding(query)
                if query_embedding:
                    # Use Supabase vector search (requires pgvector extension)
                    # Note: This assumes you have pgvector enabled and proper indexing
                    result = self.client.rpc(
                        'match_memories',
                        {
                            'query_embedding': query_embedding,
                            'match_threshold': 0.78,
                            'match_count': limit
                        }
                    ).execute()
                    
                    if result.data:
                        return [self._dict_to_entry(row) for row in result.data]
            
            # Fallback to text-based search
            result = self.client.table(self.table_name).select("*").or_(
                f"query.ilike.%{query}%,response.ilike.%{query}%,skill_used.ilike.%{query}%"
            ).order("timestamp", desc=True).limit(limit).execute()
            
            return [self._dict_to_entry(row) for row in result.data]
            
        except Exception as e:
            print(f"Warning: Memory search failed: {e}")
            return self._find_local_fallback(query, limit)
    
    def get_recent_memories(self, account_id: str = None, limit: int = 10) -> List[MemoryEntry]:
        """Get recent memories, optionally filtered by account"""
        if not self.client:
            return self._get_recent_local_fallback(account_id, limit)
        
        try:
            query = self.client.table(self.table_name).select("*")
            
            if account_id:
                query = query.eq("account_id", account_id)
            
            result = query.order("timestamp", desc=True).limit(limit).execute()
            return [self._dict_to_entry(row) for row in result.data]
            
        except Exception as e:
            print(f"Warning: Recent memories retrieval failed: {e}")
            return self._get_recent_local_fallback(account_id, limit)
    
    def get_successful_patterns(self, skill_name: str = None, limit: int = 10) -> List[MemoryEntry]:
        """Get successful execution patterns for learning"""
        if not self.client:
            return []
        
        try:
            query = self.client.table(self.table_name).select("*").eq("success", True)
            
            if skill_name:
                query = query.eq("skill_used", skill_name)
            
            result = query.order("timestamp", desc=True).limit(limit).execute()
            return [self._dict_to_entry(row) for row in result.data]
            
        except Exception as e:
            print(f"Warning: Pattern retrieval failed: {e}")
            return []
    
    def _dict_to_entry(self, data: Dict[str, Any]) -> MemoryEntry:
        """Convert dictionary to MemoryEntry"""
        return MemoryEntry(**{k: v for k, v in data.items() if k in MemoryEntry.__dataclass_fields__})
    
    def _store_local_fallback(self, entry: MemoryEntry) -> bool:
        """Fallback to local file storage"""
        try:
            local_memory_file = "/tmp/aiden_memory.jsonl"
            with open(local_memory_file, "a", encoding="utf-8") as f:
                data = asdict(entry)
                if not data.get("timestamp"):
                    data["timestamp"] = time.time()
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Warning: Local memory fallback failed: {e}")
            return False
    
    def _find_local_fallback(self, query: str, limit: int) -> List[MemoryEntry]:
        """Fallback to local file search"""
        try:
            local_memory_file = "/tmp/aiden_memory.jsonl"
            if not os.path.exists(local_memory_file):
                return []
            
            matches = []
            query_lower = query.lower()
            
            with open(local_memory_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if any(query_lower in str(data.get(field, "")).lower() 
                              for field in ["query", "response", "skill_used"]):
                            matches.append(self._dict_to_entry(data))
                    except Exception:
                        continue
            
            return sorted(matches, key=lambda x: x.timestamp or 0, reverse=True)[:limit]
            
        except Exception as e:
            print(f"Warning: Local search fallback failed: {e}")
            return []
    
    def _get_recent_local_fallback(self, account_id: str, limit: int) -> List[MemoryEntry]:
        """Fallback to get recent from local file"""
        try:
            local_memory_file = "/tmp/aiden_memory.jsonl"
            if not os.path.exists(local_memory_file):
                return []
            
            entries = []
            with open(local_memory_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if not account_id or data.get("account_id") == account_id:
                            entries.append(self._dict_to_entry(data))
                    except Exception:
                        continue
            
            return sorted(entries, key=lambda x: x.timestamp or 0, reverse=True)[:limit]
            
        except Exception as e:
            print(f"Warning: Local recent fallback failed: {e}")
            return []

# Global memory instance
memory_system = SupabaseMemory()
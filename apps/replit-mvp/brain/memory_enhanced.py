"""
AIDEN ENHANCED MEMORY SYSTEM v2
Smart memory with vector search, fallbacks, and learning patterns
"""
from __future__ import annotations
import os
import json
import pickle
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    Client = object
    SUPABASE_AVAILABLE = False
    def create_client(*a, **k): 
        raise RuntimeError("Supabase not installed: pip install supabase")

try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBEDDINGS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    LOCAL_EMBEDDINGS_AVAILABLE = False

@dataclass
class MemoryEntry:
    query: str
    plan: Dict[str, Any]
    tools_used: List[str]
    outcome: str
    artifacts: Dict[str, Any]
    cost_usd: float
    execution_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    embedding: Optional[List[float]] = None

class EnhancedMemorySystem:
    """Production-grade memory with multiple fallback strategies"""
    
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        
        # Initialize clients
        self._supabase_client: Optional[Client] = None
        self._local_embedder: Optional[SentenceTransformer] = None
        self._local_cache_file = os.path.join(os.path.dirname(__file__), "local_memory.pkl")
        self._local_memory: List[MemoryEntry] = []
        
        # Load local cache
        self._load_local_cache()
        
    def _get_supabase_client(self) -> Optional[Client]:
        """Get Supabase client with error handling"""
        if not SUPABASE_AVAILABLE or not self.supabase_url or not self.supabase_key:
            return None
        
        if self._supabase_client is None:
            try:
                self._supabase_client = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                return None
        
        return self._supabase_client
    
    def _get_local_embedder(self) -> Optional[SentenceTransformer]:
        """Get local sentence transformer with lazy loading"""
        if not LOCAL_EMBEDDINGS_AVAILABLE:
            return None
        
        if self._local_embedder is None:
            try:
                self._local_embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load local embeddings model: {e}")
                return None
        
        return self._local_embedder
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding with multiple fallback strategies"""
        # Strategy 1: OpenAI embeddings (best quality)
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[text]
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"OpenAI embeddings failed: {e}")
        
        # Strategy 2: Local sentence transformers
        embedder = self._get_local_embedder()
        if embedder:
            try:
                embedding = embedder.encode([text])[0].tolist()
                return embedding
            except Exception as e:
                print(f"Local embeddings failed: {e}")
        
        # Strategy 3: Simple hash-based "embedding" (last resort)
        text_hash = hashlib.md5(text.lower().encode()).hexdigest()
        # Convert hex to pseudo-embedding (not ideal but works for exact matches)
        return [float(int(char, 16)) / 15.0 for char in text_hash[:384]]  # 384-dim
    
    def _load_local_cache(self):
        """Load local memory cache from disk"""
        if os.path.exists(self._local_cache_file):
            try:
                with open(self._local_cache_file, 'rb') as f:
                    self._local_memory = pickle.load(f)
            except Exception as e:
                print(f"Failed to load local memory cache: {e}")
                self._local_memory = []
        else:
            self._local_memory = []
    
    def _save_local_cache(self):
        """Save local memory cache to disk"""
        try:
            os.makedirs(os.path.dirname(self._local_cache_file), exist_ok=True)
            with open(self._local_cache_file, 'wb') as f:
                pickle.dump(self._local_memory, f)
        except Exception as e:
            print(f"Failed to save local memory cache: {e}")
    
    def save_memory(self, 
                   query: str,
                   plan: Dict[str, Any],
                   tools_used: List[str],
                   outcome: str,
                   artifacts: Dict[str, Any],
                   cost_usd: float = 0.0,
                   execution_time_seconds: float = 0.0,
                   success: bool = True,
                   error_message: Optional[str] = None) -> bool:
        """Save memory entry with multiple fallback storage"""
        
        # Create memory entry
        embedding = self._get_embedding(query)
        entry = MemoryEntry(
            query=query,
            plan=plan,
            tools_used=tools_used,
            outcome=outcome,
            artifacts=artifacts,
            cost_usd=cost_usd,
            execution_time_seconds=execution_time_seconds,
            success=success,
            error_message=error_message,
            embedding=embedding
        )
        
        saved_somewhere = False
        
        # Strategy 1: Save to Supabase (primary)
        client = self._get_supabase_client()
        if client:
            try:
                data = asdict(entry)
                # Remove embedding if no pgvector support
                if not self._has_vector_support():
                    data.pop('embedding', None)
                
                result = client.table("agent_memories").insert(data).execute()
                if result.data:
                    saved_somewhere = True
                    print("Memory saved to Supabase")
            except Exception as e:
                print(f"Failed to save to Supabase: {e}")
        
        # Strategy 2: Save to local cache (fallback)
        try:
            self._local_memory.append(entry)
            # Keep only last 1000 entries locally
            if len(self._local_memory) > 1000:
                self._local_memory = self._local_memory[-1000:]
            self._save_local_cache()
            saved_somewhere = True
            print("Memory saved to local cache")
        except Exception as e:
            print(f"Failed to save to local cache: {e}")
        
        return saved_somewhere
    
    def find_similar_memories(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """Find similar memories with multiple search strategies"""
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return self._keyword_fallback_search(query, top_k)
        
        # Strategy 1: Supabase vector search (if available)
        client = self._get_supabase_client()
        if client and self._has_vector_support():
            try:
                # PostgreSQL with pgvector similarity search
                result = client.table("agent_memories") \
                    .select("*") \
                    .order("embedding <-> %s" % query_embedding) \
                    .limit(top_k) \
                    .execute()
                
                if result.data:
                    memories = []
                    for item in result.data:
                        memories.append(MemoryEntry(**item))
                    return memories
            except Exception as e:
                print(f"Supabase vector search failed: {e}")
        
        # Strategy 2: Local similarity search
        return self._local_similarity_search(query_embedding, top_k)
    
    def _local_similarity_search(self, query_embedding: List[float], top_k: int) -> List[MemoryEntry]:
        """Local cosine similarity search"""
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            if not a or not b or len(a) != len(b):
                return 0.0
            
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        
        scored_memories = []
        for memory in self._local_memory:
            if memory.embedding:
                similarity = cosine_similarity(query_embedding, memory.embedding)
                scored_memories.append((similarity, memory))
        
        # Sort by similarity (descending) and return top_k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:top_k]]
    
    def _keyword_fallback_search(self, query: str, top_k: int) -> List[MemoryEntry]:
        """Simple keyword-based search fallback"""
        query_words = set(query.lower().split())
        scored_memories = []
        
        for memory in self._local_memory:
            memory_text = f"{memory.query} {' '.join(memory.tools_used)} {memory.outcome}".lower()
            memory_words = set(memory_text.split())
            
            # Simple word overlap score
            overlap = len(query_words.intersection(memory_words))
            if overlap > 0:
                scored_memories.append((overlap, memory))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:top_k]]
    
    def get_successful_patterns(self, tool_name: str, top_k: int = 3) -> List[MemoryEntry]:
        """Get successful execution patterns for a specific tool"""
        patterns = []
        for memory in self._local_memory:
            if memory.success and tool_name in memory.tools_used:
                patterns.append(memory)
        
        # Sort by cost efficiency (success with lower cost is better)
        patterns.sort(key=lambda x: x.cost_usd)
        return patterns[:top_k]
    
    def _has_vector_support(self) -> bool:
        """Check if Supabase has pgvector enabled"""
        client = self._get_supabase_client()
        if not client:
            return False
        
        try:
            # Try to query with vector operation
            result = client.table("agent_memories").select("id").limit(1).execute()
            return True  # Basic check - would need actual vector column test
        except Exception:
            return False

# Global memory system instance
memory_system = EnhancedMemorySystem()

def save_execution_memory(query: str, plan: Dict, tools: List[str], outcome: str, 
                         artifacts: Dict, cost: float = 0.0, duration: float = 0.0, 
                         success: bool = True, error: Optional[str] = None) -> bool:
    """Convenience function to save execution memory"""
    return memory_system.save_memory(
        query=query, plan=plan, tools_used=tools, outcome=outcome,
        artifacts=artifacts, cost_usd=cost, execution_time_seconds=duration,
        success=success, error_message=error
    )

def find_similar_solutions(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Find similar past solutions"""
    memories = memory_system.find_similar_memories(query, limit)
    return [
        {
            "query": m.query,
            "tools_used": m.tools_used,
            "outcome": m.outcome,
            "artifacts": m.artifacts,
            "cost_usd": m.cost_usd,
            "success": m.success
        }
        for m in memories
    ]
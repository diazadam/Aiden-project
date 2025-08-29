"""
AidenAI Power Planner - Enhanced execution planning with smart tool selection
"""
from __future__ import annotations
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

from .toolcards import pick_relevant_cards, get_high_risk_skills
from .memory_supabase import memory_system, MemoryEntry
from .capability_manifest import build_capability_manifest

@dataclass
class ExecutionPlan:
    query: str
    tool_chain: List[str]
    steps: List[Dict[str, Any]]
    estimated_cost: float
    risk_level: str
    requires_approval: bool
    similar_memories: List[MemoryEntry]

def plan_and_execute(user_query: str, account_id: str = "local", use_memory: bool = True) -> Dict[str, Any]:
    """Main power planner function - creates plan and executes with safety controls"""
    
    # Step 1: Build execution plan
    plan = create_execution_plan(user_query, account_id, use_memory)
    
    # Step 2: Execute plan with safety controls
    if plan.requires_approval:
        return {
            "ok": False,
            "message": f"Plan requires approval. Estimated cost: ${plan.estimated_cost:.2f}",
            "plan": plan,
            "requires_approval": True
        }
    
    # Step 3: Execute the plan
    results = execute_plan_safely(plan, account_id)
    
    # Step 4: Store successful execution in memory
    if results.get("success") and use_memory:
        memory_entry = MemoryEntry(
            query=user_query,
            response=results.get("message", ""),
            skill_used=",".join(plan.tool_chain),
            account_id=account_id,
            success=True,
            cost_usd=results.get("actual_cost", 0.0),
            artifacts=results.get("artifacts", {})
        )
        memory_system.store_memory(memory_entry)
    
    return results

def create_execution_plan(user_query: str, account_id: str = "local", use_memory: bool = True) -> ExecutionPlan:
    """Create a detailed execution plan with smart tool selection"""
    
    # Get system capabilities
    manifest = build_capability_manifest()
    
    # Pick relevant tools
    relevant_tools = pick_relevant_cards(user_query, k=6)
    
    # Find similar past executions
    similar_memories = []
    if use_memory:
        similar_memories = memory_system.find_similar_memories(user_query, limit=3)
    
    # Analyze risk and cost
    high_risk_skills = get_high_risk_skills()
    requires_approval = any(tool in high_risk_skills for tool in relevant_tools)
    
    # Estimate cost based on tools
    estimated_cost = estimate_execution_cost(relevant_tools, user_query)
    
    # Determine risk level
    risk_level = "high" if requires_approval else "medium" if estimated_cost > 1.0 else "low"
    
    # Generate execution steps
    steps = generate_execution_steps(user_query, relevant_tools, manifest, similar_memories)
    
    return ExecutionPlan(
        query=user_query,
        tool_chain=relevant_tools,
        steps=steps,
        estimated_cost=estimated_cost,
        risk_level=risk_level,
        requires_approval=requires_approval,
        similar_memories=similar_memories
    )

def generate_execution_steps(user_query: str, tools: List[str], manifest: Dict, memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
    """Generate detailed execution steps using AI planning"""
    
    if not OPENAI_AVAILABLE:
        return [{"step": 1, "action": "execute_tools", "tools": tools, "note": "AI planning not available"}]
    
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\n\nSimilar past executions:\n"
            for i, mem in enumerate(memories[:2], 1):
                memory_context += f"{i}. Query: {mem.query}\n   Result: {mem.response}\n   Tools: {mem.skill_used}\n"
        
        system_prompt = f"""You are AidenAI's execution planner. Create a detailed step-by-step execution plan.

Available tools: {', '.join(tools)}
System capabilities: {manifest.get('power_statement', '')}

{memory_context}

Return a JSON array of execution steps with this format:
[
  {{"step": 1, "action": "tool_name", "description": "What this step does", "args": {{"key": "value"}}}},
  {{"step": 2, "action": "another_tool", "description": "Next action", "args": {{"key": "value"}}}}
]

Focus on concrete, executable steps that map to available tools."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create execution plan for: {user_query}"}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse response
        plan_text = response.choices[0].message.content
        if plan_text.startswith("```json"):
            plan_text = plan_text.split("```json")[1].split("```")[0]
        elif plan_text.startswith("```"):
            plan_text = plan_text.split("```")[1]
        
        steps = json.loads(plan_text.strip())
        return steps if isinstance(steps, list) else [{"step": 1, "action": "fallback", "description": "Plan parsing failed"}]
        
    except Exception as e:
        print(f"Warning: AI planning failed: {e}")
        return [{"step": 1, "action": "execute_query", "description": user_query, "tools": tools}]

def estimate_execution_cost(tools: List[str], query: str) -> float:
    """Estimate cost of executing the tool chain"""
    
    # Base cost estimates per tool
    tool_costs = {
        "bigquery_query": 5.0,  # Varies widely by query
        "gcs_upload": 0.1,      # Minimal storage cost
        "cloud_run_deploy": 2.0, # Build and deployment
        "mobile_expo_build_ios": 3.0, # EAS build minutes
        "browser": 0.5,         # Minimal compute
        "web_site_builder": 0.1, # Local generation
        "web_fetch": 0.05,      # HTTP requests
        "image_watermark": 0.1,  # Local processing
    }
    
    total_cost = 0.0
    for tool in tools:
        base_cost = tool_costs.get(tool, 0.1)
        
        # Adjust based on query complexity
        if len(query) > 500:  # Complex queries cost more
            base_cost *= 1.5
        
        total_cost += base_cost
    
    return round(total_cost, 2)

def execute_plan_safely(plan: ExecutionPlan, account_id: str) -> Dict[str, Any]:
    """Execute the plan with safety controls and monitoring"""
    
    from skills.runtime import run_skill
    from datetime import datetime
    
    results = {
        "success": True,
        "message": "Plan executed successfully",
        "artifacts": {},
        "actual_cost": 0.0,
        "steps_completed": 0,
        "execution_time": 0
    }
    
    start_time = datetime.now()
    
    try:
        for i, step in enumerate(plan.steps, 1):
            action = step.get("action")
            args = step.get("args", {})
            description = step.get("description", "")
            
            print(f"Executing step {i}: {description}")
            
            # Check if this is a valid tool
            if action in plan.tool_chain:
                # Execute the skill
                result = run_skill(action, account_id=account_id, args=args)
                
                if not result.ok:
                    results["success"] = False
                    results["message"] = f"Step {i} failed: {result.message}"
                    break
                
                # Collect artifacts
                if result.data:
                    results["artifacts"][f"step_{i}_{action}"] = result.data
                
                # Estimate cost (simplified)
                results["actual_cost"] += estimate_execution_cost([action], plan.query) / len(plan.steps)
            
            results["steps_completed"] = i
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time"] = execution_time
        
        if results["success"]:
            results["message"] = f"Successfully executed {results['steps_completed']} steps in {execution_time:.1f}s"
        
    except Exception as e:
        results["success"] = False
        results["message"] = f"Execution failed: {str(e)[:200]}"
        results["error"] = str(e)
    
    return results

def get_execution_history(account_id: str = None, limit: int = 10) -> List[MemoryEntry]:
    """Get recent execution history for analysis"""
    return memory_system.get_recent_memories(account_id, limit)

def analyze_success_patterns(skill_name: str = None) -> Dict[str, Any]:
    """Analyze successful execution patterns for optimization"""
    patterns = memory_system.get_successful_patterns(skill_name, limit=20)
    
    if not patterns:
        return {"message": "No execution patterns found"}
    
    # Analyze common patterns
    common_queries = {}
    common_tools = {}
    avg_cost = 0.0
    
    for pattern in patterns:
        # Count query types
        query_type = pattern.query[:50] + "..." if len(pattern.query) > 50 else pattern.query
        common_queries[query_type] = common_queries.get(query_type, 0) + 1
        
        # Count tool usage
        if pattern.skill_used:
            for tool in pattern.skill_used.split(","):
                tool = tool.strip()
                common_tools[tool] = common_tools.get(tool, 0) + 1
        
        # Average cost
        avg_cost += pattern.cost_usd
    
    avg_cost /= len(patterns) if patterns else 1
    
    return {
        "total_patterns": len(patterns),
        "average_cost": round(avg_cost, 2),
        "most_common_queries": sorted(common_queries.items(), key=lambda x: x[1], reverse=True)[:5],
        "most_used_tools": sorted(common_tools.items(), key=lambda x: x[1], reverse=True)[:5],
        "success_rate": "100%"  # These are already filtered for successful patterns
    }
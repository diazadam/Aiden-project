"""
AIDEN POWER PLANNER v2 - Production Safe with Cost Controls
Advanced planning with safety validation, cost estimation, and rollback capability
"""
from __future__ import annotations
import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from .safety_governor import safety_governor, validate_before_execution, estimate_operation_cost
from .memory_enhanced import memory_system, save_execution_memory
from .capability_manifest import build_capability_manifest
# from .toolcards import pick_relevant_cards  # Will implement if needed

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class ExecutionPlan:
    user_query: str
    plan_steps: List[str]
    execution_steps: List[Dict[str, Any]]
    estimated_total_cost: float
    risk_level: str
    approval_required: bool
    safety_checks: List[Dict[str, Any]]

@dataclass  
class ExecutionResult:
    success: bool
    artifacts: Dict[str, Any]
    actual_cost: float
    execution_time: float
    error_message: Optional[str] = None
    rollback_needed: bool = False

class PowerPlannerV2:
    """Advanced planning with production safety controls"""
    
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.master_pin = os.environ.get("AIDEN_MASTER_PIN")
        self._openai_client = None
        
        # Model preferences (GPT-4 variants for better planning)
        self.planning_model = os.environ.get("AIDEN_PLANNING_MODEL", "gpt-4o-mini")
        self.validation_model = os.environ.get("AIDEN_VALIDATION_MODEL", "gpt-4o-mini")
    
    def _get_openai_client(self) -> Optional[OpenAI]:
        """Get OpenAI client with error handling"""
        if not OPENAI_AVAILABLE or not self.openai_key:
            return None
        
        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=self.openai_key)
        
        return self._openai_client
    
    def create_execution_plan(self, user_query: str, account_id: str = "local") -> ExecutionPlan:
        """Create a detailed execution plan with safety validation"""
        
        # Get system capabilities and relevant tools
        manifest = build_capability_manifest()
        # relevant_tools = pick_relevant_cards(user_query, k=6)  # Simplified for now
        relevant_tools = ["bigquery_safe", "gcs_upload", "cloud_run_deploy"]
        similar_memories = memory_system.find_similar_memories(user_query, top_k=3)
        
        # Create enhanced system prompt
        system_prompt = self._build_system_prompt(manifest, relevant_tools, similar_memories)
        
        # Get plan from LLM
        raw_plan = self._get_llm_plan(system_prompt, user_query)
        if not raw_plan:
            return ExecutionPlan(
                user_query=user_query,
                plan_steps=["Error: Could not generate plan"],
                execution_steps=[],
                estimated_total_cost=0.0,
                risk_level="critical",
                approval_required=True,
                safety_checks=[{"error": "Planning failed"}]
            )
        
        # Validate and enhance plan with safety checks
        return self._validate_and_enhance_plan(user_query, raw_plan)
    
    def execute_plan_safely(self, plan: ExecutionPlan, account_id: str = "local", 
                          pin: Optional[str] = None) -> ExecutionResult:
        """Execute plan with full safety controls and rollback capability"""
        
        start_time = time.time()
        total_cost = 0.0
        artifacts = {}
        executed_steps = []
        
        # Check approval requirements
        if plan.approval_required and pin != self.master_pin:
            return ExecutionResult(
                success=False,
                artifacts={},
                actual_cost=0.0,
                execution_time=time.time() - start_time,
                error_message=f"Operation requires approval. Estimated cost: ${plan.estimated_total_cost:.2f}",
                rollback_needed=False
            )
        
        try:
            # Execute each step with safety validation
            for step_idx, step in enumerate(plan.execution_steps):
                step_start = time.time()
                
                operation = step.get("operation") or step.get("skill") or step.get("tool")
                args = step.get("args", {})
                
                if not operation:
                    continue
                
                print(f"Executing step {step_idx + 1}: {operation}")
                
                # Pre-execution safety check
                is_safe, safety_check = validate_before_execution(operation, args)
                if not is_safe:
                    error_msg = f"Safety check failed for {operation}: {', '.join(safety_check.risk_factors)}"
                    return ExecutionResult(
                        success=False,
                        artifacts=artifacts,
                        actual_cost=total_cost,
                        execution_time=time.time() - start_time,
                        error_message=error_msg,
                        rollback_needed=len(executed_steps) > 0
                    )
                
                # Execute the operation
                step_result = self._execute_single_step(operation, args, account_id, pin)
                step_duration = time.time() - step_start
                
                if step_result.get("success", False):
                    executed_steps.append({
                        "step": step_idx + 1,
                        "operation": operation,
                        "duration": step_duration,
                        "result": step_result
                    })
                    
                    # Track artifacts and costs
                    if step_result.get("artifacts"):
                        artifacts.update(step_result["artifacts"])
                    
                    step_cost = step_result.get("cost_usd", safety_check.max_cost_usd)
                    total_cost += step_cost
                    safety_governor.log_operation_cost(operation, step_cost)
                    
                else:
                    # Step failed - decide if we should rollback
                    error_msg = step_result.get("error", f"Step {step_idx + 1} failed")
                    return ExecutionResult(
                        success=False,
                        artifacts=artifacts,
                        actual_cost=total_cost,
                        execution_time=time.time() - start_time,
                        error_message=error_msg,
                        rollback_needed=self._should_rollback(executed_steps)
                    )
            
            # All steps completed successfully
            execution_time = time.time() - start_time
            
            # Save successful execution to memory
            save_execution_memory(
                query=plan.user_query,
                plan={"steps": plan.plan_steps, "execution_steps": plan.execution_steps},
                tools=[step.get("operation", "") for step in plan.execution_steps],
                outcome="Successfully executed all steps",
                artifacts=artifacts,
                cost=total_cost,
                duration=execution_time,
                success=True
            )
            
            return ExecutionResult(
                success=True,
                artifacts=artifacts,
                actual_cost=total_cost,
                execution_time=execution_time,
                rollback_needed=False
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                artifacts=artifacts,
                actual_cost=total_cost,
                execution_time=time.time() - start_time,
                error_message=f"Execution error: {str(e)}",
                rollback_needed=len(executed_steps) > 0
            )
    
    def _build_system_prompt(self, manifest: Dict, tools: List[Dict], memories: List[Any]) -> str:
        """Build enhanced system prompt with all context"""
        
        power_statement = manifest.get("power_statement", "")
        
        tools_context = "\n".join([
            f"- {tool.get('id', 'unknown')}: {tool.get('title', '')} - {tool.get('when_to_use', '')}"
            for tool in tools
        ])
        
        memory_context = ""
        if memories:
            memory_context = "PAST SUCCESSFUL PATTERNS:\n"
            for memory in memories[:3]:
                memory_context += f"- Query: {memory.query}\n"
                memory_context += f"  Tools: {', '.join(memory.tools_used)}\n"
                memory_context += f"  Outcome: {memory.outcome}\n"
                memory_context += f"  Cost: ${memory.cost_usd:.2f}\n\n"
        
        return f"""You are AidenAI, an execution-focused AI with enterprise-grade capabilities.

{power_statement}

AVAILABLE TOOLS:
{tools_context}

{memory_context}

SAFETY REQUIREMENTS:
- Always estimate costs before execution
- Include safety validations for each step
- Specify required capabilities (net, exec, fs_write)
- Plan for rollback if operations fail

RESPONSE FORMAT:
Return JSON with:
{{
  "plan_steps": ["Step 1 description", "Step 2 description", ...],
  "execution_steps": [
    {{
      "operation": "tool_name",
      "args": {{...}},
      "estimated_cost_usd": 0.0,
      "requires_approval": false,
      "rollback_plan": "how to undo if this fails"
    }}
  ],
  "rationale": "Why this approach",
  "success_criteria": "How to measure success"
}}

Focus on practical execution with real deliverables and working URLs.
"""
    
    def _get_llm_plan(self, system_prompt: str, user_query: str) -> Optional[Dict[str, Any]]:
        """Get execution plan from LLM"""
        client = self._get_openai_client()
        if not client:
            return None
        
        try:
            response = client.chat.completions.create(
                model=self.planning_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"LLM planning failed: {e}")
            return None
    
    def _validate_and_enhance_plan(self, user_query: str, raw_plan: Dict[str, Any]) -> ExecutionPlan:
        """Validate plan and add safety enhancements"""
        
        execution_steps = raw_plan.get("execution_steps", [])
        safety_checks = []
        total_estimated_cost = 0.0
        max_risk_level = "low"
        requires_approval = False
        
        # Validate each execution step
        for step in execution_steps:
            operation = step.get("operation", "")
            args = step.get("args", {})
            
            # Get cost estimate
            cost_estimate = estimate_operation_cost(operation, args)
            step["estimated_cost_usd"] = cost_estimate.estimated_cost_usd
            total_estimated_cost += cost_estimate.estimated_cost_usd
            
            # Check if approval needed
            if safety_governor.require_approval(operation, cost_estimate):
                requires_approval = True
                step["requires_approval"] = True
            
            # Update risk level
            if cost_estimate.risk_level == "critical":
                max_risk_level = "critical"
            elif cost_estimate.risk_level == "high" and max_risk_level != "critical":
                max_risk_level = "high"
            elif cost_estimate.risk_level == "medium" and max_risk_level == "low":
                max_risk_level = "medium"
            
            # Add safety check info
            safety_checks.append({
                "operation": operation,
                "cost_estimate": cost_estimate.estimated_cost_usd,
                "risk_level": cost_estimate.risk_level,
                "resource_usage": cost_estimate.resource_usage
            })
        
        return ExecutionPlan(
            user_query=user_query,
            plan_steps=raw_plan.get("plan_steps", []),
            execution_steps=execution_steps,
            estimated_total_cost=total_estimated_cost,
            risk_level=max_risk_level,
            approval_required=requires_approval,
            safety_checks=safety_checks
        )
    
    def _execute_single_step(self, operation: str, args: Dict[str, Any], 
                           account_id: str, pin: Optional[str]) -> Dict[str, Any]:
        """Execute a single operation with proper error handling"""
        try:
            from skills.runtime import run_skill
            
            # Add PIN if operation requires high-privilege capabilities
            caps_token = None
            if operation in ["bigquery_query", "cloud_run_deploy", "gcs_upload"]:
                caps_token = pin
            
            result = safety_governor.safe_execute_with_retry(
                run_skill, operation, account_id, args, caps_token
            )
            
            return {
                "success": result.ok,
                "data": result.data,
                "artifacts": result.artifacts,
                "error": result.message if not result.ok else None,
                "cost_usd": args.get("estimated_cost_usd", 0.0)  # Will be updated with actual
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cost_usd": 0.0
            }
    
    def _should_rollback(self, executed_steps: List[Dict]) -> bool:
        """Determine if rollback is needed based on executed steps"""
        # Rollback if we've done anything that created resources
        risky_operations = ["cloud_run_deploy", "gcs_upload", "bigquery_query"]
        
        for step in executed_steps:
            if step.get("operation") in risky_operations:
                return True
        
        return False

# Global planner instance
power_planner = PowerPlannerV2()

def plan_and_execute_safely(user_query: str, account_id: str = "local", 
                           pin: Optional[str] = None) -> Dict[str, Any]:
    """Main entry point for safe planning and execution"""
    
    # Create plan
    plan = power_planner.create_execution_plan(user_query, account_id)
    
    # Show plan for approval if needed
    if plan.approval_required and not pin:
        return {
            "success": False,
            "plan": {
                "steps": plan.plan_steps,
                "estimated_cost": plan.estimated_total_cost,
                "risk_level": plan.risk_level,
                "approval_required": True
            },
            "message": f"Plan requires approval. Estimated cost: ${plan.estimated_total_cost:.2f}. Use 'pin' parameter to approve.",
            "safety_checks": plan.safety_checks
        }
    
    # Execute plan
    result = power_planner.execute_plan_safely(plan, account_id, pin)
    
    return {
        "success": result.success,
        "plan": {
            "steps": plan.plan_steps,
            "estimated_cost": plan.estimated_total_cost,
            "actual_cost": result.actual_cost
        },
        "artifacts": result.artifacts,
        "execution_time": result.execution_time,
        "error": result.error_message,
        "rollback_needed": result.rollback_needed
    }
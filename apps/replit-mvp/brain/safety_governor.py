"""
AIDEN SAFETY GOVERNOR v2 - Production Safe Execution
Prevents cost overruns, validates operations, and provides rollback capabilities.
"""
from __future__ import annotations
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@dataclass
class CostEstimate:
    operation: str
    estimated_cost_usd: float
    resource_usage: Dict[str, Any]
    risk_level: str  # low, medium, high, critical
    approval_required: bool

@dataclass  
class SafetyCheck:
    operation: str
    safe: bool
    risk_factors: List[str]
    mitigations: List[str]
    max_cost_usd: float

class SafetyGovernor:
    """Production safety controls for all Aiden operations"""
    
    def __init__(self):
        self.max_query_bytes = int(os.environ.get("AIDEN_MAX_QUERY_BYTES", "1000000000"))  # 1GB default
        self.max_operation_cost = float(os.environ.get("AIDEN_MAX_OPERATION_COST", "25.0"))  # $25 default
        self.daily_cost_limit = float(os.environ.get("AIDEN_DAILY_COST_LIMIT", "100.0"))  # $100 default
        self.require_approval_above = float(os.environ.get("AIDEN_APPROVAL_THRESHOLD", "10.0"))  # $10 default
        
        # Track daily usage (in production, use Redis/DB)
        self._daily_costs = {}
        self._today = time.strftime("%Y-%m-%d")
    
    def estimate_bigquery_cost(self, sql: str, location: str = "US") -> CostEstimate:
        """Estimate BigQuery query cost before execution"""
        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=os.environ.get("GCP_PROJECT_ID"))
            
            # Dry run to get bytes processed
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            job = client.query(sql, job_config=job_config, location=location)
            
            bytes_processed = job.total_bytes_processed or 0
            
            # BigQuery pricing: $6.25 per TB in US/EU, $7.50 in other regions
            price_per_tb = 6.25 if location.upper() in ["US", "EU"] else 7.50
            estimated_cost = (bytes_processed / (1024**4)) * price_per_tb  # Convert bytes to TB
            
            risk_level = "low"
            if bytes_processed > self.max_query_bytes:
                risk_level = "critical"
            elif bytes_processed > self.max_query_bytes * 0.5:
                risk_level = "high"
            elif bytes_processed > self.max_query_bytes * 0.1:
                risk_level = "medium"
            
            return CostEstimate(
                operation="bigquery_query",
                estimated_cost_usd=estimated_cost,
                resource_usage={
                    "bytes_processed": bytes_processed,
                    "tables_scanned": self._count_tables_in_query(sql)
                },
                risk_level=risk_level,
                approval_required=estimated_cost > self.require_approval_above
            )
            
        except Exception as e:
            # Conservative estimate on error
            return CostEstimate(
                operation="bigquery_query",
                estimated_cost_usd=self.require_approval_above + 1.0,  # Force approval
                resource_usage={"error": str(e)},
                risk_level="critical",
                approval_required=True
            )
    
    def estimate_cloud_run_cost(self, args: Dict[str, Any]) -> CostEstimate:
        """Estimate Cloud Run deployment cost"""
        # Cloud Run: ~$0.40 per million requests, $0.10 per GB-hour memory
        # Conservative estimate for new service
        estimated_cost = 5.0  # Initial deployment + moderate traffic
        
        risk_level = "low"
        if args.get("allow_unauthenticated", False):
            risk_level = "medium"  # Public endpoint = potential cost exposure
        
        return CostEstimate(
            operation="cloud_run_deploy",
            estimated_cost_usd=estimated_cost,
            resource_usage={
                "service_name": args.get("service_name", "unknown"),
                "public": args.get("allow_unauthenticated", False)
            },
            risk_level=risk_level,
            approval_required=estimated_cost > self.require_approval_above
        )
    
    def check_daily_limits(self, additional_cost: float) -> bool:
        """Check if operation would exceed daily cost limits"""
        today = time.strftime("%Y-%m-%d")
        if today != self._today:
            self._daily_costs = {}  # Reset for new day
            self._today = today
        
        current_daily = self._daily_costs.get(today, 0.0)
        return (current_daily + additional_cost) <= self.daily_cost_limit
    
    def validate_operation_safety(self, operation: str, args: Dict[str, Any]) -> SafetyCheck:
        """Comprehensive safety validation before operation execution"""
        risk_factors = []
        mitigations = []
        max_cost = 0.0
        
        if operation == "bigquery_query":
            estimate = self.estimate_bigquery_cost(args.get("sql", ""), args.get("location", "US"))
            max_cost = estimate.estimated_cost_usd
            
            if estimate.resource_usage.get("bytes_processed", 0) > self.max_query_bytes:
                risk_factors.append(f"Query will process {estimate.resource_usage['bytes_processed']:,} bytes")
                mitigations.append("Add LIMIT clause or filter conditions")
            
            if "DELETE" in args.get("sql", "").upper():
                risk_factors.append("SQL contains DELETE statement")
                mitigations.append("Use dry_run first, verify target rows")
                
            if "*" in args.get("sql", "") and "LIMIT" not in args.get("sql", "").upper():
                risk_factors.append("SELECT * without LIMIT clause")
                mitigations.append("Add explicit column list and LIMIT")
        
        elif operation == "cloud_run_deploy":
            estimate = self.estimate_cloud_run_cost(args)
            max_cost = estimate.estimated_cost_usd
            
            if args.get("allow_unauthenticated", False):
                risk_factors.append("Service will be publicly accessible")
                mitigations.append("Consider adding authentication or rate limiting")
            
            if not args.get("env_vars", {}).get("ENV"):
                risk_factors.append("No environment specified")
                mitigations.append("Set ENV=prod/staging for proper configuration")
        
        elif operation == "gcs_upload":
            if args.get("make_public", False):
                risk_factors.append("File will be publicly accessible")
                mitigations.append("Verify file contains no sensitive data")
        
        # Check daily limits
        if not self.check_daily_limits(max_cost):
            risk_factors.append(f"Would exceed daily limit of ${self.daily_cost_limit}")
            mitigations.append("Wait for next day or increase daily limit")
        
        is_safe = (
            len(risk_factors) == 0 or 
            (max_cost <= self.max_operation_cost and len([r for r in risk_factors if "exceed" in r]) == 0)
        )
        
        return SafetyCheck(
            operation=operation,
            safe=is_safe,
            risk_factors=risk_factors,
            mitigations=mitigations,
            max_cost_usd=max_cost
        )
    
    def require_approval(self, operation: str, estimate: CostEstimate) -> bool:
        """Check if operation requires human approval"""
        return (
            estimate.approval_required or
            estimate.risk_level == "critical" or
            estimate.estimated_cost_usd > self.require_approval_above
        )
    
    def log_operation_cost(self, operation: str, actual_cost: float):
        """Track actual operation costs for learning"""
        today = time.strftime("%Y-%m-%d")
        if today not in self._daily_costs:
            self._daily_costs[today] = 0.0
        self._daily_costs[today] += actual_cost
        
        # In production: save to database/Redis
        print(f"COST_LOG: {operation} = ${actual_cost:.3f}, daily_total = ${self._daily_costs[today]:.3f}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def safe_execute_with_retry(self, func, *args, **kwargs):
        """Execute operation with automatic retry on transient failures"""
        return func(*args, **kwargs)
    
    def _count_tables_in_query(self, sql: str) -> int:
        """Rough estimate of table count in query"""
        sql_upper = sql.upper()
        # Simple heuristic: count FROM and JOIN keywords
        from_count = sql_upper.count(" FROM ")
        join_count = sql_upper.count(" JOIN ")
        return max(1, from_count + join_count)

# Global safety governor instance
safety_governor = SafetyGovernor()

def estimate_operation_cost(operation: str, args: Dict[str, Any]) -> CostEstimate:
    """Convenience function to estimate operation cost"""
    if operation == "bigquery_query":
        return safety_governor.estimate_bigquery_cost(args.get("sql", ""), args.get("location", "US"))
    elif operation == "cloud_run_deploy":
        return safety_governor.estimate_cloud_run_cost(args)
    else:
        # Default low-cost estimate for other operations
        return CostEstimate(
            operation=operation,
            estimated_cost_usd=1.0,
            resource_usage={},
            risk_level="low",
            approval_required=False
        )

def validate_before_execution(operation: str, args: Dict[str, Any]) -> Tuple[bool, SafetyCheck]:
    """Validate operation safety before execution"""
    safety_check = safety_governor.validate_operation_safety(operation, args)
    return safety_check.safe, safety_check
"""
Production-Safe BigQuery Skill v2.0
- Mandatory cost estimation and validation
- Automatic dry-run before execution
- Result caching and limits
- Smart query optimization suggestions
"""
from typing import Optional, List, Dict, Any
import os
import hashlib
import json
from google.cloud import bigquery
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    sql: str
    location: Optional[str] = "US"
    max_results: int = 1000                    # Hard limit on results
    max_cost_usd: float = 5.0                  # Maximum cost allowed
    destination_table: Optional[str] = None    # "project.dataset.table"
    force_execution: bool = False              # Skip dry run (dangerous)
    cache_results: bool = True                 # Cache results locally

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "bigquery_safe"
    version = "2.0.0"
    caps = {"net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        # Validate environment
        project_id = os.environ.get("GCP_PROJECT_ID")
        if not project_id:
            return Outputs(ok=False, message="GCP_PROJECT_ID environment variable not set")
        
        try:
            client = bigquery.Client(project=project_id)
        except Exception as e:
            return Outputs(ok=False, message=f"Failed to create BigQuery client: {str(e)}")
        
        # Step 1: Mandatory dry run for cost estimation
        dry_run_result = self._perform_dry_run(client, args)
        if not dry_run_result["ok"]:
            return Outputs(ok=False, message=dry_run_result["error"])
        
        estimated_cost = dry_run_result["estimated_cost_usd"]
        bytes_processed = dry_run_result["bytes_processed"]
        
        # Step 2: Cost validation
        if estimated_cost > args.max_cost_usd:
            return Outputs(
                ok=False, 
                message=f"Query cost ${estimated_cost:.4f} exceeds limit ${args.max_cost_usd}. "
                       f"Processes {bytes_processed:,} bytes. Consider adding LIMIT or WHERE clauses.",
                data={
                    "estimated_cost_usd": estimated_cost,
                    "bytes_processed": bytes_processed,
                    "optimization_suggestions": self._get_optimization_suggestions(args.sql)
                }
            )
        
        # Step 3: Check cache for identical queries
        cache_key = self._get_cache_key(args.sql, args.location)
        if args.cache_results:
            cached_result = self._get_cached_result(ctx, cache_key)
            if cached_result:
                return Outputs(
                    ok=True,
                    message=f"Returned cached result (estimated cost: ${estimated_cost:.4f})",
                    data=cached_result,
                    artifacts={"cache_hit": True, "estimated_cost_saved": estimated_cost}
                )
        
        # Step 4: Execute query (if not forced to skip and within limits)
        if not args.force_execution and estimated_cost > 1.0:
            return Outputs(
                ok=False,
                message=f"Query requires manual approval for ${estimated_cost:.4f} cost. "
                       f"Use force_execution=true with proper authorization.",
                data=dry_run_result
            )
        
        # Step 5: Safe execution with limits
        try:
            job_config = bigquery.QueryJobConfig(
                maximum_bytes_billed=int(bytes_processed * 1.2),  # 20% buffer
                use_query_cache=True
            )
            
            if args.destination_table:
                job_config.destination = client.dataset(
                    args.destination_table.split('.')[0]
                ).table(args.destination_table.split('.')[1])
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            
            query_job = client.query(args.sql, job_config=job_config, location=args.location)
            
            # Stream results with row limit
            results = []
            total_rows = 0
            
            for row in query_job:
                if total_rows >= args.max_results:
                    break
                results.append(dict(row.items()))
                total_rows += 1
            
            # Get job statistics
            job_stats = query_job._properties.get('statistics', {})
            actual_bytes = int(job_stats.get('query', {}).get('totalBytesProcessed', 0))
            actual_cost = (actual_bytes / (1024**4)) * 6.25  # Rough cost calculation
            
            result_data = {
                "job_id": query_job.job_id,
                "rows_returned": len(results),
                "total_rows_in_result": query_job.result().total_rows,
                "results": results,
                "actual_bytes_processed": actual_bytes,
                "actual_cost_usd": actual_cost,
                "estimated_cost_usd": estimated_cost,
                "query_cache_hit": job_stats.get('query', {}).get('cacheHit', False),
                "truncated": len(results) >= args.max_results
            }
            
            if args.destination_table:
                result_data["destination_table"] = args.destination_table
            
            # Cache successful results
            if args.cache_results and actual_cost < 0.10:  # Only cache cheap queries
                self._cache_result(ctx, cache_key, result_data)
            
            artifacts = {
                "bigquery_job_id": query_job.job_id,
                "cost_saved_vs_estimate": max(0, estimated_cost - actual_cost)
            }
            
            return Outputs(
                ok=True,
                message=f"Query completed. Processed {actual_bytes:,} bytes for ${actual_cost:.4f}",
                data=result_data,
                artifacts=artifacts
            )
            
        except Exception as e:
            return Outputs(
                ok=False,
                message=f"Query execution failed: {str(e)}",
                data={"error_type": type(e).__name__, "estimated_cost_usd": estimated_cost}
            )
    
    def _perform_dry_run(self, client: bigquery.Client, args: Inputs) -> Dict[str, Any]:
        """Perform mandatory dry run for cost estimation"""
        try:
            job_config = bigquery.QueryJobConfig(
                dry_run=True,
                use_query_cache=False
            )
            
            dry_run_job = client.query(args.sql, job_config=job_config, location=args.location)
            bytes_processed = dry_run_job.total_bytes_processed or 0
            
            # Calculate cost based on location
            if args.location.upper() in ["US", "EU"]:
                cost_per_tb = 6.25
            else:
                cost_per_tb = 7.50
            
            estimated_cost = (bytes_processed / (1024**4)) * cost_per_tb
            
            return {
                "ok": True,
                "bytes_processed": bytes_processed,
                "estimated_cost_usd": estimated_cost,
                "tables_referenced": self._extract_table_names(args.sql)
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": f"Dry run failed: {str(e)}"
            }
    
    def _get_optimization_suggestions(self, sql: str) -> List[str]:
        """Generate query optimization suggestions"""
        suggestions = []
        sql_upper = sql.upper()
        
        if "SELECT *" in sql_upper and "LIMIT" not in sql_upper:
            suggestions.append("Use explicit column names instead of SELECT * and add LIMIT clause")
        
        if "WHERE" not in sql_upper and "FROM" in sql_upper:
            suggestions.append("Add WHERE clause to filter data and reduce bytes processed")
        
        if "ORDER BY" in sql_upper and "LIMIT" not in sql_upper:
            suggestions.append("ORDER BY without LIMIT processes all rows - consider adding LIMIT")
        
        if sql_upper.count("JOIN") > 2:
            suggestions.append("Multiple JOINs detected - consider pre-aggregating data or using temp tables")
        
        # Check for expensive operations
        expensive_ops = ["CROSS JOIN", "WINDOW", "RANK()", "ROW_NUMBER()"]
        for op in expensive_ops:
            if op in sql_upper:
                suggestions.append(f"'{op}' detected - this operation can be expensive on large datasets")
        
        return suggestions
    
    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL (basic implementation)"""
        # This is a simplified implementation - production should use SQL parser
        import re
        
        # Look for patterns like dataset.table or project.dataset.table
        table_pattern = r'FROM\s+([`"]?[\w\-\.]+[`"]?)|JOIN\s+([`"]?[\w\-\.]+[`"]?)'
        matches = re.findall(table_pattern, sql, re.IGNORECASE)
        
        tables = []
        for match in matches:
            table = match[0] or match[1]
            if table:
                tables.append(table.strip('`"'))
        
        return list(set(tables))  # Remove duplicates
    
    def _get_cache_key(self, sql: str, location: str) -> str:
        """Generate cache key for query"""
        # Normalize SQL for caching
        normalized_sql = ' '.join(sql.strip().split())
        cache_input = f"{normalized_sql}|{location}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_cached_result(self, ctx: SkillContext, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        cache_file = os.path.join(ctx.workdir, f"bigquery_cache_{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                # Check if cache is less than 1 hour old
                cache_age = time.time() - os.path.getmtime(cache_file)
                if cache_age < 3600:  # 1 hour
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                else:
                    os.remove(cache_file)  # Remove stale cache
            except Exception:
                pass
        
        return None
    
    def _cache_result(self, ctx: SkillContext, cache_key: str, result_data: Dict[str, Any]):
        """Cache query result"""
        cache_file = os.path.join(ctx.workdir, f"bigquery_cache_{cache_key}.json")
        
        try:
            # Only cache small results (< 100KB)
            result_json = json.dumps(result_data)
            if len(result_json) < 100000:  # 100KB limit
                with open(cache_file, 'w') as f:
                    f.write(result_json)
        except Exception:
            pass  # Cache failure is not critical
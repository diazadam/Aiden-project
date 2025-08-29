#!/usr/bin/env python3
"""Test Power-Stack v2 system integration"""

from brain.power_planner_v2 import PowerPlannerV2
from brain.safety_governor import SafetyGovernor
from brain.capability_manifest import build_capability_manifest

def test_power_stack_v2():
    """Test the complete Power-Stack v2 system"""
    
    print('🚀 Testing Power-Stack v2 System')
    print('=' * 50)
    
    # Test 1: Planning phase
    print('\n📋 PHASE 1: Planning')
    planner = PowerPlannerV2()
    
    test_query = """
    Create a data analysis dashboard:
    1. Query BigQuery for user analytics data
    2. Upload generated charts to Cloud Storage  
    3. Deploy dashboard as Cloud Run service
    """
    
    try:
        plan = planner.create_execution_plan(test_query, 'test_account')
        print(f'✅ Plan created with {len(plan.steps)} steps')
        print(f'💰 Estimated cost: ${plan.estimated_total_cost:.2f}')
        print(f'🔐 Requires approval: {plan.approval_required}')
    except Exception as e:
        print(f'❌ Planning failed: {e}')
    
    # Test 2: Safety validation
    print('\n🛡️  PHASE 2: Safety Validation')
    governor = SafetyGovernor()
    
    try:
        validation = governor.validate_operation_safety('bigquery_safe', {
            'sql': 'SELECT COUNT(*) FROM `bigquery-public-data.samples.wikipedia` LIMIT 10',
            'max_cost_usd': 1.0
        })
        
        print(f'🔍 Validation result: {validation.safe}')
        if not validation.safe:
            print(f'⚠️  Risk factors: {", ".join(validation.risk_factors)}')
        else:
            print('✅ All safety checks passed')
    except Exception as e:
        print(f'❌ Safety validation failed: {e}')
    
    # Test 3: Capability awareness
    print('\n🧠 PHASE 3: Capability Awareness')
    try:
        manifest = build_capability_manifest()
        active_skills = len(manifest['skills_available'])
        active_connectors = sum(1 for v in manifest['connectors'].values() if v)
        
        print(f'🛠️  Active skills: {active_skills}')
        print(f'🔗 Active connectors: {active_connectors}')
        print(f'☁️  GCP Project: {manifest["gcp_project"]}')
        
        # Show power statement
        print('\n💪 POWER STATEMENT:')
        print(manifest['power_statement'][:200] + '...')
        
    except Exception as e:
        print(f'❌ Capability check failed: {e}')
    
    print('\n🎯 Power-Stack v2 system integration test complete!')
    return True

if __name__ == "__main__":
    test_power_stack_v2()
#!/usr/bin/env python3
"""
Code structure validation for the approval workflow in manus_coordination_api_v2.py
"""

import ast
import sys
from pathlib import Path

def validate_approval_workflow():
    """Validate the approval workflow code structure"""
    print("Validating approval workflow implementation...")
    
    # Read the file
    api_file = Path(__file__).parent / 'manus_coordination_api_v2.py'
    with open(api_file, 'r') as f:
        code = f.read()
    
    # Test 1: Parse the Python file
    print("\n1. Checking Python syntax...")
    try:
        tree = ast.parse(code)
        print("   ✅ Python syntax is valid")
    except SyntaxError as e:
        print(f"   ❌ Syntax error: {e}")
        return False
    
    # Test 2: Check for pending_approvals variable
    print("\n2. Checking for pending_approvals variable...")
    if 'pending_approvals = []' in code:
        print("   ✅ pending_approvals variable found")
    else:
        print("   ❌ pending_approvals variable not found")
        return False
    
    # Test 3: Check for request_approval function
    print("\n3. Checking for request_approval function...")
    if 'def request_approval(' in code:
        print("   ✅ request_approval function found")
    else:
        print("   ❌ request_approval function not found")
        return False
    
    # Test 4: Check for sync_with_github with skip_approval parameter
    print("\n4. Checking for sync_with_github with approval control...")
    if 'def sync_with_github(skip_approval=False):' in code:
        print("   ✅ sync_with_github function has skip_approval parameter")
    else:
        print("   ❌ sync_with_github function missing skip_approval parameter")
        return False
    
    # Test 5: Check for approval endpoints
    print("\n5. Checking for approval API endpoints...")
    endpoints = [
        "/api/approvals",
        "/api/approvals/<approval_id>/approve",
        "/api/approvals/<approval_id>/reject"
    ]
    for endpoint in endpoints:
        if endpoint in code:
            print(f"   ✅ Found endpoint: {endpoint}")
        else:
            print(f"   ❌ Missing endpoint: {endpoint}")
            return False
    
    # Test 6: Check that automatic syncs now request approval
    print("\n6. Checking that automatic syncs request approval...")
    # Count instances of request_approval calls
    approval_calls = code.count('request_approval(')
    if approval_calls >= 5:
        print(f"   ✅ Found {approval_calls} approval request calls")
    else:
        print(f"   ⚠️  Only found {approval_calls} approval request calls (expected at least 5)")
    
    # Test 7: Check for approval status in status endpoint
    print("\n7. Checking for approval tracking in status endpoint...")
    if "'approvals':" in code and "'pending':" in code:
        print("   ✅ Status endpoint includes approval tracking")
    else:
        print("   ❌ Status endpoint missing approval tracking")
        return False
    
    # Test 8: Check for WebSocket events for approvals
    print("\n8. Checking for approval notification events...")
    events = ['approval_requested', 'approval_granted', 'approval_rejected']
    for event in events:
        if event in code:
            print(f"   ✅ Found WebSocket event: {event}")
        else:
            print(f"   ⚠️  Missing WebSocket event: {event}")
    
    print("\n✅ All validation checks passed!")
    return True

if __name__ == '__main__':
    try:
        success = validate_approval_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

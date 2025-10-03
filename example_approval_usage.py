#!/usr/bin/env python3
"""
Example Usage: MANUS Coordination API - Approval Workflow

This script demonstrates how to interact with the approval workflow
using the MANUS Coordination API.
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:5001/api"

def example_1_check_pending_approvals():
    """Example 1: Check for pending approval requests"""
    print("\n" + "="*60)
    print("Example 1: Checking Pending Approvals")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/approvals?status=pending")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['pending_count']} pending approval(s)")
        
        for approval in data['approvals']:
            print(f"\n  ID: {approval['id']}")
            print(f"  Action: {approval['action_type']}")
            print(f"  Description: {approval['description']}")
            print(f"  Requested by: {approval['requested_by']}")
            print(f"  Requested at: {approval['requested_at']}")
    else:
        print(f"❌ Error: {response.status_code}")

def example_2_approve_request(approval_id, approver="manus_2"):
    """Example 2: Approve a pending request"""
    print("\n" + "="*60)
    print(f"Example 2: Approving Request {approval_id}")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/approvals/{approval_id}/approve",
        json={"approver": approver}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Approval granted!")
        print(f"  Approved by: {data['approval']['approved_by']}")
        print(f"  Approved at: {data['approval']['approved_at']}")
        print(f"  Status: {data['approval']['status']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.json()}")

def example_3_reject_request(approval_id, approver="manus_2", reason="Needs review"):
    """Example 3: Reject a pending request"""
    print("\n" + "="*60)
    print(f"Example 3: Rejecting Request {approval_id}")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/approvals/{approval_id}/reject",
        json={
            "approver": approver,
            "reason": reason
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"❌ Approval rejected")
        print(f"  Rejected by: {data['approval']['rejected_by']}")
        print(f"  Rejected at: {data['approval']['rejected_at']}")
        print(f"  Reason: {data['approval']['rejection_reason']}")
        print(f"  Status: {data['approval']['status']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.json()}")

def example_4_manual_sync_with_approval():
    """Example 4: Trigger a manual sync with approval"""
    print("\n" + "="*60)
    print("Example 4: Manual Sync with Approval")
    print("="*60)
    
    # First request the approval
    response = requests.post(
        f"{API_BASE_URL}/sync",
        json={"manus_id": "manus_2", "approved": False}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"📋 Approval requested")
        print(f"  Approval ID: {data['approval_id']}")
        print(f"  Message: {data['message']}")
        
        # Now approve it
        approval_id = data['approval_id']
        print(f"\n⏳ Approving request {approval_id}...")
        time.sleep(1)
        
        approve_response = requests.post(
            f"{API_BASE_URL}/approvals/{approval_id}/approve",
            json={"approver": "manus_2"}
        )
        
        if approve_response.status_code == 200:
            print("✅ Sync approved and executed!")
        else:
            print(f"❌ Approval failed: {approve_response.json()}")
    else:
        print(f"❌ Error: {response.status_code}")

def example_5_check_system_status():
    """Example 5: Check system status including approvals"""
    print("\n" + "="*60)
    print("Example 5: System Status with Approval Metrics")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/status")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 System Status:")
        print(f"  Active Manus: {data['active_manus']}")
        print(f"  Total Tasks: {data['tasks']['total']}")
        print(f"  Available Tasks: {data['tasks']['available']}")
        print(f"  Claimed Tasks: {data['tasks']['claimed']}")
        print(f"  Complete Tasks: {data['tasks']['complete']}")
        
        print(f"\n✅ Approval Metrics:")
        print(f"  Pending: {data['approvals']['pending']}")
        print(f"  Approved: {data['approvals']['approved']}")
        print(f"  Rejected: {data['approvals']['rejected']}")
    else:
        print(f"❌ Error: {response.status_code}")

def example_6_complete_task_workflow():
    """Example 6: Complete workflow - Task completion with approval"""
    print("\n" + "="*60)
    print("Example 6: Complete Task Workflow with Approval")
    print("="*60)
    
    # Simulate task completion (this would normally come from a Manus)
    print("\n1. Task completion triggers approval request...")
    print("   (In real scenario, Manus calls /api/tasks/complete)")
    
    # Check for new approval requests
    print("\n2. Checking for pending approvals...")
    response = requests.get(f"{API_BASE_URL}/approvals?status=pending")
    
    if response.status_code == 200:
        data = response.json()
        if data['pending_count'] > 0:
            approval = data['approvals'][0]
            print(f"   Found pending approval: {approval['id']}")
            print(f"   Description: {approval['description']}")
            
            # Approve it
            print("\n3. Manus #2 reviews and approves...")
            approve_response = requests.post(
                f"{API_BASE_URL}/approvals/{approval['id']}/approve",
                json={"approver": "manus_2"}
            )
            
            if approve_response.status_code == 200:
                print("   ✅ Approved! Changes will be pushed to GitHub.")
            else:
                print(f"   ❌ Approval failed: {approve_response.json()}")
        else:
            print("   No pending approvals found")
    else:
        print(f"   ❌ Error: {response.status_code}")

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("MANUS Coordination API - Approval Workflow Examples")
    print("="*60)
    print("\nNote: These examples assume the API server is running at:")
    print(f"      {API_BASE_URL}")
    print("\nPress Ctrl+C to exit at any time.")
    
    try:
        # Run examples
        example_1_check_pending_approvals()
        example_5_check_system_status()
        
        # Interactive examples (commented out by default)
        # Uncomment to run:
        # example_2_approve_request("APPROVAL-1")
        # example_3_reject_request("APPROVAL-2", reason="Changes need review")
        # example_4_manual_sync_with_approval()
        # example_6_complete_task_workflow()
        
        print("\n" + "="*60)
        print("Examples completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print(f"   Make sure the server is running at {API_BASE_URL}")
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()

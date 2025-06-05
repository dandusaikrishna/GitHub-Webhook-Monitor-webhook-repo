#!/usr/bin/env python3
"""
Test script for GitHub Webhook Monitor
This script simulates GitHub webhook events to test the application
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
API_URL = "http://localhost:5000/api/events"
HEALTH_URL = "http://localhost:5000/health"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def create_push_payload():
    """Create a sample PUSH webhook payload"""
    return {
        "ref": "refs/heads/main",
        "head_commit": {
            "id": "abc123def456",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author": {
                "name": "Test User"
            }
        },
        "pusher": {
            "name": "Test User"
        },
        "repository": {
            "name": "test-repo",
            "full_name": "testuser/test-repo"
        }
    }

def create_pull_request_payload(action="opened"):
    """Create a sample PULL REQUEST webhook payload"""
    return {
        "action": action,
        "pull_request": {
            "id": 12345,
            "user": {
                "login": "test-contributor"
            },
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "merged_at": datetime.now(timezone.utc).isoformat() if action == "merged" else None,
            "merged_by": {
                "login": "test-maintainer"
            } if action == "merged" else None
        }
    }

def send_webhook_event(payload, event_type):
    """Send a webhook event to the application"""
    headers = {
        "X-GitHub-Event": event_type,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, 
                               json=payload, 
                               headers=headers, 
                               timeout=10)
        return response
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return None

def test_push_event():
    """Test PUSH webhook event"""
    print("📤 Testing PUSH event...")
    payload = create_push_payload()
    response = send_webhook_event(payload, "push")
    
    if response and response.status_code == 200:
        print("✅ PUSH event processed successfully")
        return True
    else:
        print(f"❌ PUSH event failed: {response.status_code if response else 'No response'}")
        return False

def test_pull_request_event():
    """Test PULL REQUEST webhook event"""
    print("🔄 Testing PULL REQUEST event...")
    payload = create_pull_request_payload("opened")
    response = send_webhook_event(payload, "pull_request")
    
    if response and response.status_code == 200:
        print("✅ PULL REQUEST event processed successfully")
        return True
    else:
        print(f"❌ PULL REQUEST event failed: {response.status_code if response else 'No response'}")
        return False

def test_merge_event():
    """Test MERGE webhook event (merged pull request)"""
    print("⚡ Testing MERGE event...")
    payload = create_pull_request_payload("merged")
    response = send_webhook_event(payload, "pull_request")
    
    if response and response.status_code == 200:
        print("✅ MERGE event processed successfully")
        return True
    else:
        print(f"❌ MERGE event failed: {response.status_code if response else 'No response'}")
        return False

def test_api_endpoint():
    """Test the events API endpoint"""
    print("📊 Testing API endpoint...")
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ API endpoint working - Retrieved {len(events)} events")
            
            # Display recent events
            if events:
                print("\n📋 Recent events:")
                for i, event in enumerate(events[:3]):  # Show first 3 events
                    action = event.get('action', 'UNKNOWN')
                    author = event.get('author', 'Unknown')
                    timestamp = event.get('timestamp', 'Unknown time')
                    print(f"  {i+1}. [{action}] {author} - {timestamp}")
            
            return True
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API endpoint error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting GitHub Webhook Monitor Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("PUSH Event", test_push_event),
        ("PULL REQUEST Event", test_pull_request_event),
        ("MERGE Event", test_merge_event),
        ("API Endpoint", test_api_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
        
        # Wait a bit between tests
        time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your webhook monitor is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the application logs.")
    
    return passed == len(results)

def simulate_real_activity():
    """Simulate real GitHub activity over time"""
    print("\n🎭 Simulating real GitHub activity...")
    
    activities = [
        ("push", "main", "Added new feature"),
        ("pull_request", "feature/auth", "Authentication system"),
        ("push", "develop", "Bug fixes"),
        ("pull_request", "hotfix/security", "Security patch"),
        ("merge", "feature/auth", "Merged authentication")
    ]
    
    for i, (action, branch, description) in enumerate(activities):
        print(f"🔄 Simulating {action} to {branch}: {description}")
        
        if action == "push":
            payload = create_push_payload()
            payload["ref"] = f"refs/heads/{branch}"
            send_webhook_event(payload, "push")
        elif action == "pull_request":
            payload = create_pull_request_payload("opened")
            payload["pull_request"]["head"]["ref"] = branch
            send_webhook_event(payload, "pull_request")
        elif action == "merge":
            payload = create_pull_request_payload("merged")
            payload["pull_request"]["head"]["ref"] = branch
            send_webhook_event(payload, "pull_request")
        
        # Wait between activities to simulate real timing
        if i < len(activities) - 1:
            print("⏱️  Waiting 3 seconds...")
            time.sleep(3)
    
    print("✅ Activity simulation completed!")

if __name__ == "__main__":
    print("🔧 GitHub Webhook Monitor Test Suite")
    print("Make sure your application is running on http://localhost:5000")
    print()
    
    # Ask user what they want to do
    print("Select test mode:")
    print("1. Quick test (health + basic functionality)")
    print("2. Comprehensive test (all endpoints)")
    print("3. Simulate real activity")
    print("4. All of the above")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_health_check()
            test_api_endpoint()
        elif choice == "2":
            run_comprehensive_test()
        elif choice == "3":
            simulate_real_activity()
        elif choice == "4":
            run_comprehensive_test()
            print("\n" + "="*50)
            simulate_real_activity()
        else:
            print("Invalid choice. Running comprehensive test...")
            run_comprehensive_test()
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    print("\n🏁 Testing completed. Check your webhook monitor UI at http://localhost:5000\n")

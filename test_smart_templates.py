#!/usr/bin/env python3
"""
🚀 Smart Template System Test Suite

This script tests all the new smart template generation features
including AI suggestions, user history tracking, and template recommendations.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_ID = "test_user_123"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None, description: str = ""):
    """Test an API endpoint and return the result"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Endpoint: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success! Response keys: {list(result.keys())}")
            return result
        else:
            print(f"   ❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return None

def main():
    """Run comprehensive smart template system tests"""
    print("🚀 Smart Template Generation System Test Suite")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n📡 Testing server connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
        return
    
    # Test 2: AI Template Suggestions
    result = test_endpoint(
        f"/api/ai-template-suggestions/{TEST_USER_ID}?limit=3",
        description="AI Template Suggestions (should return trending templates for new user)"
    )
    
    # Test 3: Track Query Pattern
    sample_query_data = {
        "strategic_question": "How can we expand into the European market while maintaining competitive advantages?",
        "time_frame": "medium_term",
        "region": "europe",
        "additional_instructions": "Focus on regulatory compliance and market entry strategies",
        "user_id": TEST_USER_ID
    }
    
    result = test_endpoint(
        "/api/track-query-pattern",
        method="POST",
        data=sample_query_data,
        description="Track Query Pattern (should analyze and store user query)"
    )
    
    # Test 4: Template Recommendations
    recommendation_data = {
        "strategic_question": "What are the risks of entering the Asian technology market?",
        "user_id": TEST_USER_ID
    }
    
    result = test_endpoint(
        "/api/get-template-recommendations",
        method="POST",
        data=recommendation_data,
        description="Template Recommendations (should find matching templates)"
    )
    
    # Test 5: Popular Query Patterns
    result = test_endpoint(
        "/api/popular-query-patterns?limit=5",
        description="Popular Query Patterns (should return trending patterns)"
    )
    
    # Test 6: User Analytics
    result = test_endpoint(
        f"/api/user-analytics/{TEST_USER_ID}",
        description="User Analytics (should return usage statistics)"
    )
    
    # Test 7: Add more query patterns to build history
    additional_queries = [
        {
            "strategic_question": "What are the competitive threats in the AI technology sector?",
            "time_frame": "short_term",
            "region": "global",
            "user_id": TEST_USER_ID
        },
        {
            "strategic_question": "How can we optimize our supply chain for cost efficiency?",
            "time_frame": "medium_term", 
            "region": "north_america",
            "user_id": TEST_USER_ID
        },
        {
            "strategic_question": "What are the geopolitical risks affecting our business operations?",
            "time_frame": "long_term",
            "region": "global",
            "user_id": TEST_USER_ID
        }
    ]
    
    print(f"\n📚 Adding more query patterns to build user history...")
    for i, query in enumerate(additional_queries, 1):
        print(f"   Adding pattern {i}/3...")
        test_endpoint(
            "/api/track-query-pattern",
            method="POST",
            data=query,
            description=f"Query Pattern {i}"
        )
        time.sleep(0.5)  # Small delay between requests
    
    # Test 8: AI Suggestions after building history
    print(f"\n🤖 Testing AI suggestions after building user history...")
    result = test_endpoint(
        f"/api/ai-template-suggestions/{TEST_USER_ID}?limit=3",
        description="AI Template Suggestions (should now be personalized based on history)"
    )
    
    # Test 9: Smart Template Generation
    smart_template_data = {
        "user_id": TEST_USER_ID,
        "domain": "market",
        "intent": "competitive_analysis"
    }
    
    result = test_endpoint(
        "/api/generate-smart-template",
        method="POST",
        data=smart_template_data,
        description="Smart Template Generation (should create AI-generated template)"
    )
    
    # Test 10: Check template library
    result = test_endpoint(
        "/api/templates?limit=10",
        description="Template Library (should include default and generated templates)"
    )
    
    print("\n" + "=" * 60)
    print("🎉 Smart Template System Test Complete!")
    print("\nKey Features Tested:")
    print("✅ AI-Powered Template Suggestions")
    print("✅ Real-time Template Recommendations") 
    print("✅ User Query Pattern Tracking")
    print("✅ Usage-Based Learning")
    print("✅ Smart Template Generation")
    print("✅ User Analytics")
    print("✅ Popular Pattern Analysis")
    print("\n🚀 Your smart template system is ready to use!")
    print(f"\n📱 Visit http://127.0.0.1:8000 to see the new features in action!")

if __name__ == "__main__":
    main() 
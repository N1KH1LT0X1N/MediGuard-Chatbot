#!/usr/bin/env python3
"""
Quick test script for MediGuard bot webhook endpoints.
Run this while mediguard_bot.py is running.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(method, path, data=None, description=""):
    """Test an endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {path}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{path}", data=data, timeout=5)
        else:
            print(f"❌ Unknown method: {method}")
            return
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            content = response.json()
            print(f"Response (JSON):")
            print(json.dumps(content, indent=2))
        except:
            print(f"Response (Text):")
            print(response.text[:500])
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS")
        else:
            print(f"⚠️ Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server")
        print("   Make sure mediguard_bot.py is running on port 5000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🧪 MediGuard Bot Webhook Test Suite")
    print("=" * 60)
    print("Make sure mediguard_bot.py is running first!")
    print("=" * 60)
    
    # Test 1: Root GET
    test_endpoint("GET", "/", description="Root endpoint (GET)")
    
    # Test 2: Root POST (should show helpful error)
    test_endpoint("POST", "/", description="Root endpoint (POST) - Should show error")
    
    # Test 3: Health check
    test_endpoint("GET", "/health", description="Health check endpoint")
    
    # Test 4: Debug endpoint
    test_endpoint("GET", "/debug", description="Debug endpoint")
    
    # Test 5: WhatsApp webhook (correct endpoint)
    test_endpoint(
        "POST", 
        "/whatsapp",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "hello"
        },
        description="WhatsApp webhook - Simulating Twilio POST"
    )
    
    # Test 6: WhatsApp webhook with biomarker data
    test_endpoint(
        "POST",
        "/whatsapp",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "/start"
        },
        description="WhatsApp webhook - Start command"
    )
    
    print("\n" + "=" * 60)
    print("✅ Test suite complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check the console output from mediguard_bot.py")
    print("2. Verify all endpoints return expected responses")
    print("3. If POST to / shows error, update Twilio webhook URL")


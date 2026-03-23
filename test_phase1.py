#!/usr/bin/env python
"""
Manual test script for Phase 1 POC

This script tests the core Ignition Gateway integration without running the FastAPI server.
Use this to verify the Ignition client works before testing the full API.
"""

import asyncio
from app.ignition_client import ignition_client


async def test_connectivity():
    """Test 1: Check Ignition Gateway connectivity"""
    print("\n" + "="*60)
    print("TEST 1: Ignition Gateway Connectivity")
    print("="*60)
    
    connected = await ignition_client.check_connectivity()
    
    if connected:
        print("✅ SUCCESS: Ignition Gateway is reachable")
    else:
        print("❌ FAILED: Cannot reach Ignition Gateway")
        print(f"   URL: {ignition_client.base_url}")
        print("   Make sure Ignition is running: docker-compose up -d")
    
    return connected


async def test_api_token():
    """Test 2: Generate API token"""
    print("\n" + "="*60)
    print("TEST 2: API Token Generation")
    print("="*60)
    
    try:
        token_response = await ignition_client.generate_api_token()
        print(f"✅ SUCCESS: API token generated")
        print(f"   Key length: {len(token_response.key)} chars")
        print(f"   Hash length: {len(token_response.hash)} chars")
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not generate API token")
        print(f"   Error: {str(e)}")
        print(f"   Check username/password in .env file")
        return False


async def test_tag_creation():
    """Test 3: Create a minimal tag"""
    print("\n" + "="*60)
    print("TEST 3: Tag Creation")
    print("="*60)
    
    try:
        quality_codes = await ignition_client.create_minimal_tag(
            tag_name="Phase1_POC_Test",
            tag_path="POC_Testing"
        )
        
        if len(quality_codes) == 0:
            print("✅ SUCCESS: Tag created successfully (empty quality codes)")
            print("   Tag path: POC_Testing/Phase1_POC_Test")
            print("   Verify in Ignition Designer Tag Browser")
        else:
            print("⚠️  WARNING: Tag import returned quality codes:")
            for i, qc in enumerate(quality_codes, 1):
                print(f"   [{i}] Level: {qc.level}")
                print(f"       Code: {qc.userCode}")
                print(f"       Message: {qc.diagnosticMessage}")
        
        return len(quality_codes) == 0
    except Exception as e:
        print(f"❌ FAILED: Could not create tag")
        print(f"   Error: {str(e)}")
        return False


async def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n" + "="*60)
    print("PHASE 1 POC - MANUAL TEST SUITE")
    print("="*60)
    print(f"Gateway URL: {ignition_client.base_url}")
    print(f"Username: {ignition_client.username}")
    print(f"SSL Verify: {ignition_client.verify_ssl}")
    
    results = {
        "connectivity": False,
        "api_token": False,
        "tag_creation": False
    }
    
    # Test 1: Connectivity
    results["connectivity"] = await test_connectivity()
    if not results["connectivity"]:
        print("\n❌ Cannot proceed without Gateway connectivity")
        return results
    
    # Test 2: API Token
    results["api_token"] = await test_api_token()
    if not results["api_token"]:
        print("\n❌ Cannot proceed without API token")
        return results
    
    # Test 3: Tag Creation
    results["tag_creation"] = await test_tag_creation()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Phase 1 POC is working!")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
    print("="*60 + "\n")
    
    return results


if __name__ == "__main__":
    print("\n🚀 Starting Phase 1 POC Tests...\n")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    results = asyncio.run(run_all_tests())
    
    # Exit with error code if any test failed
    import sys
    sys.exit(0 if all(results.values()) else 1)

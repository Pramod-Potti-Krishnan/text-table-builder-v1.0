"""
Quick Deployment Test Script
============================

Tests the Text and Table Builder API to verify deployment.
"""

import requests
import json
import sys
from typing import Dict, Any


API_URL = "http://localhost:8001/api/v1"


def test_health():
    """Test health endpoint."""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)

    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()

        data = response.json()
        print("✅ Health check passed")
        print(f"   Status: {data['status']}")
        print(f"   Service: {data['service']}")
        print(f"   Provider: {data.get('llm_provider', 'N/A')}")
        print(f"   Model: {data.get('llm_model', 'N/A')}")
        return True

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_text_generation():
    """Test text generation endpoint."""
    print("\n" + "="*80)
    print("TEST 2: Text Generation")
    print("="*80)

    request_data = {
        "presentation_id": "test_pres_001",
        "slide_id": "slide_001",
        "slide_number": 1,
        "topics": [
            "Revenue growth of 32%",
            "Market expansion into 3 new regions",
            "Cost efficiency improvements"
        ],
        "narrative": "Strong Q3 performance demonstrates exceptional growth",
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Q3 Financial Results"
        },
        "constraints": {
            "max_characters": 250,
            "style": "professional",
            "tone": "data-driven"
        }
    }

    try:
        response = requests.post(
            f"{API_URL}/generate/text",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        data = response.json()
        print("✅ Text generation successful")
        print(f"   Content length: {len(data['content'])} characters")
        print(f"   Word count: {data['metadata']['word_count']}")
        print(f"   Target: {data['metadata']['target_word_count']}")
        print(f"   Within tolerance: {data['metadata']['within_tolerance']}")
        print(f"   Generation time: {data['metadata']['generation_time_ms']:.2f}ms")
        print(f"\n   Generated HTML (first 200 chars):")
        print(f"   {data['content'][:200]}...")
        return True

    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return False


def test_table_generation():
    """Test table generation endpoint."""
    print("\n" + "="*80)
    print("TEST 3: Table Generation")
    print("="*80)

    request_data = {
        "presentation_id": "test_pres_001",
        "slide_id": "slide_002",
        "slide_number": 2,
        "description": "Regional revenue comparison showing Q2 vs Q3 performance",
        "data": {
            "Q2": {
                "North America": 45.2,
                "Europe": 32.1,
                "Asia": 28.7
            },
            "Q3": {
                "North America": 58.3,
                "Europe": 39.4,
                "Asia": 35.6
            }
        },
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Regional Performance"
        },
        "constraints": {
            "max_rows": 10,
            "max_columns": 5,
            "style": "clean"
        }
    }

    try:
        response = requests.post(
            f"{API_URL}/generate/table",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        data = response.json()
        print("✅ Table generation successful")
        print(f"   Rows: {data['metadata']['rows']}")
        print(f"   Columns: {data['metadata']['columns']}")
        print(f"   Data points: {data['metadata']['data_points']}")
        print(f"   Has header: {data['metadata']['has_header']}")
        print(f"   Generation time: {data['metadata']['generation_time_ms']:.2f}ms")
        print(f"\n   Generated HTML (first 300 chars):")
        print(f"   {data['html'][:300]}...")
        return True

    except Exception as e:
        print(f"❌ Table generation failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return False


def test_session_info():
    """Test session info endpoint."""
    print("\n" + "="*80)
    print("TEST 4: Session Info")
    print("="*80)

    try:
        response = requests.get(f"{API_URL}/session/test_pres_001")
        response.raise_for_status()

        data = response.json()
        print("✅ Session info retrieved")
        print(f"   Presentation ID: {data['presentation_id']}")
        print(f"   Slides in context: {data['slides_in_context']}")
        print(f"   Context size: {data['context_size_bytes']} bytes")
        print(f"   Last updated: {data['last_updated']}")
        return True

    except Exception as e:
        print(f"❌ Session info failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return False


def test_root():
    """Test root endpoint."""
    print("\n" + "="*80)
    print("TEST 5: Root Endpoint")
    print("="*80)

    try:
        response = requests.get(f"{API_URL.replace('/api/v1', '')}/")
        response.raise_for_status()

        data = response.json()
        print("✅ Root endpoint accessible")
        print(f"   Service: {data['service']}")
        print(f"   Version: {data['version']}")
        print(f"   Status: {data['status']}")
        return True

    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TEXT AND TABLE BUILDER - DEPLOYMENT TEST")
    print("="*80)
    print(f"Testing API at: {API_URL}")

    # Run tests
    results = {
        "Health Check": test_health(),
        "Root Endpoint": test_root(),
        "Text Generation": test_text_generation(),
        "Table Generation": test_table_generation(),
        "Session Info": test_session_info()
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print("\n" + "-"*80)
    print(f"  Total: {passed}/{total} tests passed")
    print("="*80)

    if passed == total:
        print("\n🎉 All tests passed! Deployment is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

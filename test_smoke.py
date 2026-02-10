#!/usr/bin/env python3
"""
Smoke test for Manim Web App.
Verifies basic functionality without requiring user interaction.
"""
import time
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_PROMPT = "Plot y = sin(x) on axes"


def test_server_running():
    """Check if server is accessible."""
    try:
        response = requests.get(BASE_URL, timeout=5)
        assert response.status_code == 200, f"Server returned {response.status_code}"
        print("✓ Server is running")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Server not accessible: {e}")
        return False


def test_examples_endpoint():
    """Check if examples endpoint works."""
    try:
        response = requests.get(f"{BASE_URL}/examples", timeout=5)
        assert response.status_code == 200, f"Examples endpoint returned {response.status_code}"
        examples = response.json()
        assert isinstance(examples, list), "Examples should be a list"
        assert len(examples) > 0, "Should have at least one example"
        print(f"✓ Examples endpoint working ({len(examples)} examples found)")
        return True
    except (requests.exceptions.RequestException, AssertionError) as e:
        print(f"✗ Examples endpoint failed: {e}")
        return False


def test_generate_endpoint():
    """Test animation generation (this may take a while)."""
    print(f"\nTesting generation with prompt: '{TEST_PROMPT}'")
    print("This may take 1-2 minutes...")

    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json={"prompt": TEST_PROMPT},
            timeout=180  # 3 minute timeout
        )

        assert response.status_code == 200, f"Generate returned {response.status_code}"
        result = response.json()

        if result["status"] == "success":
            print("✓ Generation successful")
            print(f"  Plan: {result.get('plan', 'N/A')[:100]}...")

            # Check if video file exists
            generated_dir = Path(__file__).parent / "generated"
            video_path = generated_dir / "latest.mp4"

            if video_path.exists() and video_path.stat().st_size > 0:
                print(f"✓ Video file created ({video_path.stat().st_size} bytes)")
                return True
            else:
                print("✗ Video file not found or empty")
                return False
        else:
            print(f"✗ Generation failed: {result.get('errors', 'Unknown error')}")
            return False

    except requests.exceptions.Timeout:
        print("✗ Generation timed out (>3 minutes)")
        return False
    except (requests.exceptions.RequestException, AssertionError) as e:
        print(f"✗ Generation test failed: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("="*60)
    print("Manim Web App - Smoke Test")
    print("="*60)
    print()

    tests = [
        ("Server Running", test_server_running),
        ("Examples Endpoint", test_examples_endpoint),
        ("Generate Endpoint", test_generate_endpoint)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 40)
        passed = test_func()
        results.append((test_name, passed))
        time.sleep(1)

    print("\n" + "="*60)
    print("Test Results")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)
    print("\n" + "="*60)

    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())

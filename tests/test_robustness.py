"""Test robustness of handle_message with edge cases"""
import sys
from mediguard_bot import handle_message

def test_edge_case(name, input_text, should_succeed=True):
    """Test an edge case and verify it returns a valid response"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Input: {repr(input_text[:100])}")
    print(f"{'='*60}")
    
    try:
        result = handle_message("test_user", input_text)
        
        # Validate response
        if not result:
            print(f"FAIL: No response returned")
            return False
        if not isinstance(result, str):
            print(f"FAIL: Response is not a string: {type(result)}")
            return False
        if len(result.strip()) == 0:
            print(f"FAIL: Empty response")
            return False
        
        print(f"SUCCESS: Got response ({len(result)} chars)")
        print(f"First 150 chars: {result[:150]}")
        return True
        
    except Exception as e:
        print(f"FAIL: Exception raised: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("ROBUSTNESS TEST SUITE")
    print("="*60)
    
    test_cases = [
        # Edge cases
        ("Empty string", ""),
        ("Whitespace only", "   \n\t  "),
        ("Very long input", "a" * 100000),  # Should be truncated
        ("None input", None),
        ("Non-string input", 12345),
        ("Special characters", "!@#$%^&*()"),
        ("Unicode characters", "测试 🧪 émojis"),
        ("Newlines only", "\n\n\n"),
        ("Mixed case commands", "HeLLo"),
        ("Command with extra spaces", "  hello  "),
        
        # Valid inputs
        ("Valid hello", "hello"),
        ("Valid help", "help"),
        ("Valid template", "template"),
        
        # Invalid JSON (should not crash)
        ("Invalid JSON - missing brace", '{"hemoglobin": 14.5'),
        ("Invalid JSON - extra comma", '{"hemoglobin": 14.5,}'),
        ("Invalid JSON - wrong type", '{"hemoglobin": "not a number"}'),
        
        # URLs
        ("Invalid URL", "http://invalid-url"),
        ("URL without extension", "https://example.com/file"),
        
        # Queries
        ("Short query", "hi"),
        ("Long query", "What is the normal range for hemoglobin in adults?"),
    ]
    
    results = {}
    for name, input_text in test_cases:
        results[name] = test_edge_case(name, input_text)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"{name:40} : {status}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    if passed == total:
        print("ALL TESTS PASSED! handle_message is robust.")
    else:
        print(f"{total - passed} tests failed. Review errors above.")
    print(f"{'='*60}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())


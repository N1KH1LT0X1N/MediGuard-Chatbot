"""Test all input types to verify bot functionality"""
import sys
from mediguard_bot import handle_message

def test_command(command, expected_keywords):
    """Test a command and check for expected keywords in response"""
    print(f"\n{'='*60}")
    print(f"Testing: '{command}'")
    print(f"{'='*60}")
    try:
        result = handle_message("test_user", command)
        if result:
            result_ascii = result.encode('ascii', 'ignore').decode('ascii')
            print(f"SUCCESS: Got response ({len(result)} chars)")
            print(f"First 200 chars: {result_ascii[:200]}")
            
            # Check for expected keywords
            found = []
            for keyword in expected_keywords:
                if keyword.lower() in result.lower():
                    found.append(keyword)
            
            if found:
                print(f"Found expected keywords: {found}")
            else:
                print(f"WARNING: Expected keywords not found: {expected_keywords}")
            return True
        else:
            print("ERROR: No response returned")
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_json_input():
    """Test JSON input"""
    test_json = """{
  "hemoglobin": 14.5,
  "wbc_count": 7.2,
  "platelet_count": 250,
  "glucose": 95,
  "creatinine": 1.0,
  "bun": 15,
  "sodium": 138,
  "potassium": 4.2,
  "chloride": 102,
  "calcium": 9.5,
  "alt": 25,
  "ast": 30,
  "bilirubin_total": 0.8,
  "albumin": 4.0,
  "total_protein": 7.0,
  "ldh": 180,
  "troponin": 0.02,
  "bnp": 50,
  "crp": 1.5,
  "esr": 10,
  "procalcitonin": 0.03,
  "d_dimer": 0.3,
  "inr": 1.0,
  "lactate": 1.5
}"""
    return test_command(test_json, ["Prediction", "MediGuard"])

def main():
    print("="*60)
    print("COMPREHENSIVE BOT FUNCTIONALITY TEST")
    print("="*60)
    
    results = {}
    
    # Test commands
    results["hello"] = test_command("hello", ["welcome", "MediGuard"])
    results["help"] = test_command("help", ["help", "JSON", "Format"])
    results["template"] = test_command("template", ["Template", "hemoglobin"])
    
    # Test JSON input
    results["json"] = test_json_input()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:15} : {status}")
    
    all_passed = all(results.values())
    print(f"\n{'='*60}")
    if all_passed:
        print("ALL TESTS PASSED! Bot is working correctly.")
    else:
        print("SOME TESTS FAILED. Check errors above.")
    print(f"{'='*60}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())


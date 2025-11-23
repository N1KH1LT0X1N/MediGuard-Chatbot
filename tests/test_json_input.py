"""Test JSON input parsing"""
from mediguard_bot import handle_message

# Test JSON input
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

print("Testing JSON input...")
result = handle_message("test_user", test_json)
print(f"Result length: {len(result) if result else 0}")
if result:
    # Use ASCII-safe printing
    safe_result = result.encode('ascii', 'ignore').decode('ascii')
    print(f"First 300 chars (ASCII-safe): {safe_result[:300]}")
    print(f"SUCCESS: JSON input processed correctly!")
else:
    print("ERROR: No result returned")


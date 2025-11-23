# 💬 MediGuard AI - Sample Conversation Flows

This document provides detailed examples of typical conversations with the MediGuard AI WhatsApp bot, demonstrating various use cases and scenarios.

---

## 📋 Table of Contents

1. [First-Time User Experience](#1-first-time-user-experience)
2. [Normal Lab Results](#2-normal-lab-results)
3. [Critical Sepsis Case](#3-critical-sepsis-case)
4. [Acute Cardiac Event](#4-acute-cardiac-event)
5. [Renal Failure Detection](#5-renal-failure-detection)
6. [Query-Based Interaction](#6-query-based-interaction)
7. [Error Handling](#7-error-handling)

---

## 1. First-Time User Experience

### Scenario: New user learns how to use the system

```
User: Hello

Bot: *Welcome to MediGuard AI! 🏥*

I'm your clinical triage assistant powered by AI. Send me blood test results and I'll provide:

• Disease prediction & confidence
• Key biomarker analysis
• Medical references
• Risk assessment

*Get started:*
Type 'template' to see input format
Type 'help' for full instructions

⚕️ This is an AI assistant for educational/triage purposes. Always consult a healthcare provider for medical decisions.

─────────────────────────────

User: template

Bot: *📋 JSON Template (copy and edit values):*

```json
{
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
}
```

Replace values with actual test results and send.

─────────────────────────────

User: help

Bot: *MediGuard AI - Clinical Triage Assistant*

*How to Submit Blood Test Values:*

*Option 1: JSON Format*
```
{
  "hemoglobin": 14.5,
  "wbc_count": 7.2,
  ...
}
```

*Option 2: Key-Value Format*
```
hemoglobin=14.5, wbc_count=7.2, ...
```

*Option 3: CSV Format*
```
14.5,7.2,250,95,1.0,15,...
```

*Required Biomarkers (24 total):*
Hemoglobin, WBC Count, Platelet Count, Glucose, Creatinine, BUN, Sodium, Potassium, Chloride, Calcium, ALT, AST, Total Bilirubin, Albumin, Total Protein, LDH, Troponin, BNP, CRP, ESR, Procalcitonin, D-Dimer, INR, Lactate

*Commands:*
• `/start` - Get started
• `template` - Get input template
• `explain more` - Detailed analysis
• `show sources` - Medical references
• `help` - Show this message
• `reset` - Clear session

⚕️ Note: This is an AI assistant for educational and triage purposes...
```

---

## 2. Normal Lab Results

### Scenario: All biomarkers within normal ranges

```
User: {
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
}

Bot: ✅ *MediGuard AI Prediction*

*Prediction:* Normal Range
*Confidence:* 99.8%
*Severity:* LOW

*📊 Probability Breakdown:*
  Normal Range: 99.8% ████████████████████
  Infection: 0.1%
  Metabolic Disorder: 0.1%

*🔬 Key Biomarkers:*
  (No abnormal biomarkers detected)

*💡 Explanation:*
All biomarkers are within normal ranges. No significant abnormalities detected.

*📚 References:*
1. Reference Ranges in Clinical Chemistry — Normal Biomarker Ranges
   _Citation: Kratz A, et al. N Engl J Med. 2004;351(15):1548-1563_

*Next Steps:*
• Review findings with a qualified healthcare provider
• For critical findings, seek immediate medical attention
• Type 'explain more' for detailed analysis
• Type 'show sources' for full references

_⚕️ Disclaimer: This AI-powered analysis is for informational purposes only and does not replace professional medical advice. Always consult a healthcare provider for medical decisions._
```

---

## 3. Critical Sepsis Case

### Scenario: Patient with severe sepsis - elevated PCT, lactate, WBC

```
User: {
  "hemoglobin": 8.5,
  "wbc_count": 18.5,
  "platelet_count": 85,
  "glucose": 180,
  "creatinine": 2.1,
  "bun": 42,
  "sodium": 132,
  "potassium": 5.2,
  "chloride": 98,
  "calcium": 8.1,
  "alt": 85,
  "ast": 120,
  "bilirubin_total": 1.8,
  "albumin": 2.8,
  "total_protein": 5.5,
  "ldh": 420,
  "troponin": 0.08,
  "bnp": 280,
  "crp": 185,
  "esr": 65,
  "procalcitonin": 5.2,
  "d_dimer": 2.8,
  "inr": 1.6,
  "lactate": 6.5
}

Bot: 🚨 *MediGuard AI Prediction*

*Prediction:* Sepsis
*Confidence:* 87.5%
*Severity:* CRITICAL

*📊 Probability Breakdown:*
  Sepsis: 87.5% ████████████████████
  Infection: 8.2% ███
  Renal Failure: 2.8% █
  Liver Disease: 1.2%
  Normal Range: 0.3%

*🔬 Key Biomarkers:*
  ↑ PCT: 5.2 ng/mL (HIGH)
  ↑ LAC: 6.5 mmol/L (HIGH)
  ↑ WBC: 18.5 ×10³/μL (HIGH)
  ↑ CRP: 185 mg/L (HIGH)
  ↓ HGB: 8.5 g/dL (LOW)

*💡 Explanation:*
Prediction indicates Sepsis. Key findings: PCT is HIGH (↑ 5.2 ng/mL), LAC is HIGH (↑ 6.5 mmol/L), WBC is HIGH (↑ 18.5 ×10³/μL). Systemic inflammatory response to infection

*⚠️ Warnings:*
  🚨 CRITICAL: Procalcitonin (PCT) is dangerously HIGH: 5.2 ng/mL
  🚨 CRITICAL: Lactate (LAC) is dangerously HIGH: 6.5 mmol/L
  ⚠️ WBC Count (WBC) is ABOVE normal range (18.5 ×10³/μL > 11.0 ×10³/μL)
  ⚠️ Hemoglobin (HGB) is BELOW normal range (8.5 g/dL < 12.0 g/dL)
  ⚠️ Platelet Count (PLT) is BELOW normal range (85 ×10³/μL < 150 ×10³/μL)
  ⚠️ CRP (CRP) is ABOVE normal range (185 mg/L > 3.0 mg/L)
  ... and 6 more warnings

*📚 References:*
1. Surviving Sepsis Campaign Guidelines — Biomarker-Guided Diagnosis
   Procalcitonin (PCT) levels >2.0 ng/mL are highly suggestive of bacterial sepsis. Lactate >4 mmol/L indicates severe sepsis with tissue hypoperfusion.
   _Citation: Rhodes A, et al. Intensive Care Med. 2017;43(3):304-377_

2. Sepsis-3 Consensus Definitions — Diagnostic Criteria
   Sepsis is defined as life-threatening organ dysfunction caused by dysregulated host response to infection. SOFA score ≥2 with suspected infection.
   _Citation: Singer M, et al. JAMA. 2016;315(8):801-810_

*Next Steps:*
• Review findings with a qualified healthcare provider
• For critical findings, seek immediate medical attention
• Type 'explain more' for detailed analysis
• Type 'show sources' for full references

_⚕️ Disclaimer: This AI-powered analysis is for informational purposes only and does not replace professional medical advice. Always consult a healthcare provider for medical decisions._

─────────────────────────────

User: explain more

Bot: *🔍 Detailed Analysis*

*Prediction:* Sepsis
*Confidence:* 87.5%
*Severity Level:* CRITICAL

*Full Explanation:*
Prediction indicates Sepsis. Key findings: PCT is HIGH (↑ 5.2 ng/mL), LAC is HIGH (↑ 6.5 mmol/L), WBC is HIGH (↑ 18.5 ×10³/μL). Systemic inflammatory response to infection

*Detailed Biomarker Analysis:*

↑ *Procalcitonin (PCT)*
  Value: 5.2 ng/mL
  Status: HIGH
  Deviation: 10300% from normal

↑ *Lactate (LAC)*
  Value: 6.5 mmol/L
  Status: HIGH
  Deviation: 345% from normal

↑ *White Blood Cell Count (WBC)*
  Value: 18.5 ×10³/μL
  Status: HIGH
  Deviation: 147% from normal

↑ *C-Reactive Protein (CRP)*
  Value: 185 mg/L
  Status: HIGH
  Deviation: 12233% from normal

↓ *Hemoglobin (HGB)*
  Value: 8.5 g/dL
  Status: LOW
  Deviation: 42% from normal

*All Disease Probabilities:*
  Sepsis: 87.5%
  Infection: 8.2%
  Renal Failure: 2.8%
  Liver Disease: 1.2%
  Coagulopathy: 0.2%
  Normal Range: 0.1%

─────────────────────────────

User: show sources

Bot: *📚 Medical References:*

1. *Surviving Sepsis Campaign Guidelines* — Biomarker-Guided Diagnosis
   Procalcitonin (PCT) levels >2.0 ng/mL are highly suggestive of bacterial sepsis. Lactate >4 mmol/L indicates severe sepsis with tissue hypoperfusion.
   _Citation: Rhodes A, et al. Intensive Care Med. 2017;43(3):304-377_

2. *Sepsis-3 Consensus Definitions* — Diagnostic Criteria
   Sepsis is defined as life-threatening organ dysfunction caused by dysregulated host response to infection. SOFA score ≥2 with suspected infection.
   _Citation: Singer M, et al. JAMA. 2016;315(8):801-810_
```

---

## 4. Acute Cardiac Event

### Scenario: Elevated troponin and BNP indicating MI/heart failure

```
User: troponin=1.5, bnp=850, ldh=620, hemoglobin=13.2, wbc_count=8.5, platelet_count=220, glucose=110, creatinine=1.1, bun=18, sodium=139, potassium=4.0, chloride=101, calcium=9.2, alt=28, ast=42, bilirubin_total=0.9, albumin=3.8, total_protein=6.8, crp=8.5, esr=22, procalcitonin=0.04, d_dimer=0.8, inr=1.1, lactate=2.0

Bot: 🚨 *MediGuard AI Prediction*

*Prediction:* Acute Cardiac Event
*Confidence:* 92.3%
*Severity:* CRITICAL

*📊 Probability Breakdown:*
  Acute Cardiac Event: 92.3% ████████████████████
  Infection: 4.2% █
  Normal Range: 2.1%
  Coagulopathy: 1.4%

*🔬 Key Biomarkers:*
  ↑ TnI: 1.5 ng/mL (HIGH)
  ↑ BNP: 850 pg/mL (HIGH)
  ↑ LDH: 620 U/L (HIGH)

*💡 Explanation:*
Prediction indicates Acute Cardiac Event. Key findings: TnI is HIGH (↑ 1.5 ng/mL), BNP is HIGH (↑ 850 pg/mL), LDH is HIGH (↑ 620 U/L). Myocardial infarction or acute heart failure

*⚠️ Warnings:*
  🚨 CRITICAL: Cardiac Troponin I (TnI) is dangerously HIGH: 1.5 ng/mL
  🚨 CRITICAL: B-Type Natriuretic Peptide (BNP) is dangerously HIGH: 850 pg/mL
  ⚠️ LDH (LDH) is ABOVE normal range (620 U/L > 280 U/L)
  ⚠️ CRP (CRP) is ABOVE normal range (8.5 mg/L > 3.0 mg/L)

*📚 References:*
1. Fourth Universal Definition of Myocardial Infarction — Troponin in Acute MI
   Cardiac troponin I >0.04 ng/mL indicates myocardial injury. Serial troponin rise/fall pattern diagnostic for acute MI.
   _Citation: Thygesen K, et al. Circulation. 2018;138(20):e618-e651_

2. Heart Failure Biomarkers — BNP and NT-proBNP
   BNP >400 pg/mL suggests acute decompensated heart failure. Elevated BNP correlates with left ventricular dysfunction severity.
   _Citation: Januzzi JL, et al. J Am Coll Cardiol. 2019;73(9):1086-1099_

*Next Steps:*
• Review findings with a qualified healthcare provider
• For critical findings, seek immediate medical attention
• Type 'explain more' for detailed analysis
• Type 'show sources' for full references

_⚕️ Disclaimer: This AI-powered analysis is for informational purposes only..._
```

---

## 5. Renal Failure Detection

### Scenario: Elevated creatinine and BUN with electrolyte imbalances

```
User: 13.8,7.8,195,102,4.2,68,141,5.8,104,9.8,32,38,1.1,3.6,6.9,195,0.03,75,3.2,15,0.05,0.4,1.1,1.8

Bot: ⚠️ *MediGuard AI Prediction*

*Prediction:* Acute Renal Failure
*Confidence:* 81.6%
*Severity:* CRITICAL

*📊 Probability Breakdown:*
  Acute Renal Failure: 81.6% ████████████████████
  Metabolic Disorder: 12.3% ████
  Normal Range: 4.1% █
  Infection: 2.0%

*🔬 Key Biomarkers:*
  ↑ CREAT: 4.2 mg/dL (HIGH)
  ↑ BUN: 68 mg/dL (HIGH)
  ↑ K: 5.8 mEq/L (HIGH)

*💡 Explanation:*
Prediction indicates Acute Renal Failure. Key findings: CREAT is HIGH (↑ 4.2 mg/dL), BUN is HIGH (↑ 68 mg/dL), K is HIGH (↑ 5.8 mEq/L). Sudden loss of kidney function

*⚠️ Warnings:*
  🚨 CRITICAL: Creatinine (CREAT) is dangerously HIGH: 4.2 mg/dL
  🚨 CRITICAL: Blood Urea Nitrogen (BUN) is dangerously HIGH: 68 mg/dL
  ⚠️ Potassium (K) is ABOVE normal range (5.8 mEq/L > 5.0 mEq/L)

*📚 References:*
1. KDIGO Acute Kidney Injury Guidelines — AKI Diagnosis
   AKI is defined by serum creatinine increase ≥0.3 mg/dL within 48h or ≥1.5× baseline within 7 days. Creatinine >2.0 mg/dL with rising trend indicates significant renal impairment.
   _Citation: KDIGO AKI Work Group. Kidney Int Suppl. 2012;2(1):1-138_

*Next Steps:*
• Review findings with a qualified healthcare provider
• For critical findings, seek immediate medical attention
• Type 'explain more' for detailed analysis
• Type 'show sources' for full references

_⚕️ Disclaimer: This AI-powered analysis is for informational purposes only..._
```

---

## 6. Query-Based Interaction

### Scenario: User asks about specific biomarkers

```
User: What does high troponin mean?

Bot: *📚 References for: "What does high troponin mean?..."*

*📚 Medical References:*

1. *Fourth Universal Definition of Myocardial Infarction* — Troponin in Acute MI
   Cardiac troponin I >0.04 ng/mL indicates myocardial injury. Serial troponin rise/fall pattern diagnostic for acute MI.
   _Citation: Thygesen K, et al. Circulation. 2018;138(20):e618-e651_

2. *Heart Failure Biomarkers* — BNP and NT-proBNP
   BNP >400 pg/mL suggests acute decompensated heart failure. Elevated BNP correlates with left ventricular dysfunction severity.
   _Citation: Januzzi JL, et al. J Am Coll Cardiol. 2019;73(9):1086-1099_
```

---

## 7. Error Handling

### Scenario: Invalid input formats and missing data

```
User: hemoglobin=14.5, wbc=7.2

Bot: I didn't understand that. Send blood test values in JSON, key=value, or CSV format.

Type 'help' for instructions or 'template' for an example.

─────────────────────────────

User: {
  "hemoglobin": 14.5,
  "wbc_count": 7.2
}

Bot: ❌ Error processing prediction: Missing biomarker value: platelet_count

Please check your input format and try again.

─────────────────────────────

User: <script>alert('xss')</script>

Bot: ⚠️ Security error: Suspicious pattern detected: <script

─────────────────────────────

User: reset

Bot: ✅ Session cleared. Send new biomarker values or type 'help'.
```

---

## 📝 Key Takeaways

### Input Formats
1. **JSON**: Best for structured, named inputs
2. **Key-Value**: Convenient for partial updates
3. **CSV**: Fastest for complete biomarker sets (must be in correct order)

### Bot Commands
- `/start` or `hello` - Welcome message
- `help` - Full instructions
- `template` - Get input examples
- `explain more` - Detailed analysis
- `show sources` - Medical references
- `reset` - Clear session

### Response Structure
Every prediction includes:
1. **Prediction** - Disease category and confidence
2. **Probability Breakdown** - All category scores
3. **Key Biomarkers** - Critical values driving prediction
4. **Explanation** - Clinical interpretation
5. **Warnings** - Out-of-range values
6. **References** - Medical literature citations
7. **Next Steps** - Recommended actions
8. **Disclaimer** - Medical liability notice

### Best Practices
- Always review predictions with healthcare providers
- Use for triage and educational purposes only
- Submit complete biomarker sets for accurate predictions
- Request 'explain more' for detailed insights
- Reference medical sources for evidence-based support

---

<p align="center">
  <strong>⚕️ MediGuard AI - Empowering Clinical Decision-Making ⚕️</strong>
</p>

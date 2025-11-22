# 🏥 MediGuard AI - Clinical Triage & Prediction System

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> AI-powered WhatsApp bot for clinical blood test analysis and disease prediction.

MediGuard AI is a sophisticated medical triage system that analyzes blood test biomarkers via WhatsApp, providing instant disease predictions, risk assessments, and medical references. Built for clinicians, nurses, and healthcare professionals.

## 🚨 Medical Disclaimer

**IMPORTANT:** MediGuard AI is designed for **educational and triage purposes only**. This system does NOT replace professional medical judgment or diagnosis. All predictions must be reviewed by qualified healthcare providers before making clinical decisions.

- ✅ Use for: Educational purposes, triage support, research, clinical decision support
- ❌ NOT for: Primary diagnosis, treatment decisions, patient self-diagnosis

## ✨ Features

- 🔬 **24 Biomarker Analysis** - Comprehensive blood test evaluation
- 🎯 **Disease Prediction** - AI-powered classification across 9 disease categories
- 📊 **Risk Assessment** - Confidence scores and probability distributions
- 🔍 **Key Biomarker Identification** - Highlights critical values driving predictions
- 📚 **Medical References** - Evidence-based citations from medical literature
- 🔒 **HIPAA-Compliant Logging** - Anonymized, secure data handling
- ⚡ **Real-time Analysis** - Instant predictions via WhatsApp
- 🛡️ **Input Validation** - Range checking and warning system

## 🧬 Supported Biomarkers (24 Total)

### Hematology
- Hemoglobin (HGB)
- White Blood Cell Count (WBC)
- Platelet Count (PLT)

### Kidney Function
- Creatinine (CREAT)
- Blood Urea Nitrogen (BUN)

### Electrolytes
- Sodium (Na), Potassium (K), Chloride (Cl), Calcium (Ca)

### Liver Function
- ALT, AST, Total Bilirubin, Albumin, Total Protein

### Cardiac Markers
- Lactate Dehydrogenase (LDH)
- Cardiac Troponin I (TnI)
- B-Type Natriuretic Peptide (BNP)

### Inflammation
- C-Reactive Protein (CRP)
- Erythrocyte Sedimentation Rate (ESR)
- Procalcitonin (PCT)

### Coagulation
- D-Dimer (DD)
- International Normalized Ratio (INR)

### Metabolism
- Blood Glucose (GLU)
- Lactate (LAC)

## 🎯 Disease Categories

1. **Sepsis** (Critical)
2. **Acute Cardiac Event** (Critical)
3. **Acute Renal Failure** (Critical)
4. **Liver Disease** (High)
5. **Metabolic Disorder** (Moderate)
6. **Coagulopathy** (High)
7. **Anemia** (Moderate)
8. **Infection** (Moderate)
9. **Normal Range** (Low)

## 📋 Requirements

- Python 3.9+
- Twilio WhatsApp account
- Google Gemini API key (optional, for enhanced explanations)
- Flask web server
- SQLite database

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/N1KH1LT0X1N/Whatsapp-Bot.git
cd Whatsapp-Bot
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GEMINI_API_KEY=your_gemini_api_key
ANONYMIZATION_SALT=generate_unique_random_string_here
```

### 4️⃣ Run MediGuard Bot

```bash
python mediguard_bot.py
```

The bot will start on `http://localhost:5000`

### 5️⃣ Expose with ngrok (for Twilio webhook)

```bash
ngrok http 5000
```

### 6️⃣ Configure Twilio Webhook

In your [Twilio Console](https://console.twilio.com/):
1. Go to Messaging → Settings → WhatsApp Sandbox
2. Set **WHEN A MESSAGE COMES IN** to:
   ```
   https://<your-ngrok-subdomain>.ngrok.io/whatsapp
   ```

## 💬 How to Use

### WhatsApp Commands

**Start the Bot:**
```
/start
hello
```

**Get Help:**
```
help
```

**Get Input Template:**
```
template
template json
template csv
```

**Submit Blood Test Values:**

**Option 1: JSON Format**
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

**Option 2: Key-Value Format**
```
hemoglobin=14.5, wbc_count=7.2, platelet_count=250, glucose=95, creatinine=1.0, bun=15, sodium=138, potassium=4.2, chloride=102, calcium=9.5, alt=25, ast=30, bilirubin_total=0.8, albumin=4.0, total_protein=7.0, ldh=180, troponin=0.02, bnp=50, crp=1.5, esr=10, procalcitonin=0.03, d_dimer=0.3, inr=1.0, lactate=1.5
```

**Option 3: CSV Format** (values in standard order)
```
14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5
```

**Get More Details:**
```
explain more
```

**View Medical References:**
```
show sources
references
```

**Reset Session:**
```
reset
```

## 📊 Example Conversation

```
You: /start
Bot: Welcome to MediGuard AI! 🏥
     I'm your clinical triage assistant...

You: template json
Bot: 📋 JSON Template (copy and edit values):
     {...}

You: {
       "hemoglobin": 8.5,
       "wbc_count": 18.5,
       "procalcitonin": 5.2,
       "lactate": 6.5,
       ...
     }

Bot: 🚨 MediGuard AI Prediction

     Prediction: Sepsis
     Confidence: 87.5%
     Severity: CRITICAL

     📊 Probability Breakdown:
       Sepsis: 87.5% ████████████████████
       Infection: 8.2% ███
       Normal Range: 2.1% █

     🔬 Key Biomarkers:
       ↑ PCT: 5.2 ng/mL (HIGH)
       ↑ LAC: 6.5 mmol/L (HIGH)
       ↑ WBC: 18.5 ×10³/μL (HIGH)
       ↓ HGB: 8.5 g/dL (LOW)

     💡 Explanation:
     Prediction indicates Sepsis. Key findings: PCT is HIGH (↑ 5.2 ng/mL),
     LAC is HIGH (↑ 6.5 mmol/L), WBC is HIGH (↑ 18.5 ×10³/μL).
     Systemic inflammatory response to infection

     ⚠️ Warnings:
       🚨 CRITICAL: Procalcitonin (PCT) is dangerously HIGH: 5.2 ng/mL
       🚨 CRITICAL: Lactate (LAC) is dangerously HIGH: 6.5 mmol/L
       ⚠️ WBC Count is ABOVE normal range

     📚 References:
     1. Surviving Sepsis Campaign Guidelines — Biomarker-Guided Diagnosis
        Citation: Rhodes A, et al. Intensive Care Med. 2017;43(3):304-377

     Next Steps:
     • Review findings with a qualified healthcare provider
     • For critical findings, seek immediate medical attention
     • Type 'explain more' for detailed analysis

     ⚕️ Disclaimer: This AI-powered analysis is for informational
     purposes only...
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│            WhatsApp User                     │
└────────────────┬────────────────────────────┘
                 │
                 ▼ Twilio WhatsApp API
┌─────────────────────────────────────────────┐
│         mediguard_bot.py (Flask)            │
│  ┌──────────────────────────────────────┐  │
│  │     /whatsapp Webhook Endpoint       │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    BiomarkerInputParser              │  │
│  │    Parse JSON/CSV/Key-Value          │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    BiomarkerScaler                   │  │
│  │    Min-Max scaling, validation       │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    MediGuardPredictor                │  │
│  │    Disease classification            │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    MedicalRAGEngine                  │  │
│  │    Retrieve medical references       │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    ResponseFormatter                 │  │
│  │    Format WhatsApp message           │  │
│  └─────────────┬────────────────────────┘  │
│                │                            │
│  ┌─────────────▼────────────────────────┐  │
│  │    SecureLogger                      │  │
│  │    Anonymized audit trail            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Whatsapp-Bot/
├── mediguard_bot.py              # Main WhatsApp bot application
├── mediguard/                    # Core MediGuard package
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── predictor.py          # Disease prediction model
│   │   └── scaler.py             # Biomarker scaling/normalization
│   ├── data/
│   │   ├── biomarkers.json       # 24 biomarker metadata
│   │   └── models/               # Saved ML models (future)
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── input_parser.py       # Parse WhatsApp input formats
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── rag_engine.py         # Medical knowledge retrieval
│   └── utils/
│       ├── __init__.py
│       ├── security.py           # Anonymization, logging
│       └── formatters.py         # WhatsApp message formatting
├── api/
│   ├── __init__.py
│   └── predict_api.py            # REST API endpoint
├── tests/
│   └── test_mediguard.py         # Test suite
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── README_MEDIGUARD.md           # This file
└── SAMPLE_CONVERSATIONS.md       # Example interactions

```

## 🔒 Security & Compliance

### Data Protection

MediGuard AI implements comprehensive security measures compliant with healthcare data protection standards:

1. **User Anonymization**
   - All user IDs (phone numbers) are SHA-256 hashed with salt
   - No PHI (Protected Health Information) stored in logs
   - Configurable data retention policies

2. **Secure Logging**
   - Only aggregated/statistical data logged
   - Automatic cleanup of expired logs
   - Audit trail for all predictions

3. **Input Validation**
   - SQL injection prevention
   - Script injection detection
   - Length and pattern validation

4. **HIPAA Considerations**
   - Anonymized data storage
   - Secure transmission (HTTPS required)
   - Minimal data retention
   - Audit logging

### Security Best Practices

```bash
# Generate strong anonymization salt
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set secure permissions on database
chmod 600 mediguard.db

# Use HTTPS in production (via reverse proxy like nginx)
# Never commit .env files to version control
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/test_mediguard.py -v
```

Run with coverage:

```bash
pytest tests/test_mediguard.py --cov=mediguard --cov-report=html
```

## 🌐 REST API

MediGuard also provides a REST API for programmatic access:

### Start API Server

```bash
python api/predict_api.py
```

API runs on `http://localhost:5001`

### API Endpoints

**POST /api/predict**
```bash
curl -X POST http://localhost:5001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "biomarkers": {
      "hemoglobin": 14.5,
      "wbc_count": 7.2,
      ...
    }
  }'
```

**GET /api/biomarkers**
```bash
curl http://localhost:5001/api/biomarkers
```

**GET /api/template?format=json**
```bash
curl http://localhost:5001/api/template?format=json
```

## 🚀 Deployment

### Deploy to Render

1. Fork this repository
2. Sign up at [Render.com](https://render.com)
3. Create new Web Service
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn mediguard_bot:app`
   - Add environment variables from `.env.example`
5. Deploy!

### Deploy to Heroku

```bash
heroku create your-mediguard-app
heroku config:set TWILIO_ACCOUNT_SID=ACxxx...
heroku config:set TWILIO_AUTH_TOKEN=xxx...
heroku config:set GEMINI_API_KEY=xxx...
heroku config:set ANONYMIZATION_SALT=xxx...
git push heroku main
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "mediguard_bot:app"]
```

```bash
docker build -t mediguard-ai .
docker run -p 5000:5000 --env-file .env mediguard-ai
```

## 📚 Medical Knowledge Base

The RAG engine includes evidence-based references from:
- Surviving Sepsis Campaign Guidelines
- Fourth Universal Definition of Myocardial Infarction
- KDIGO Acute Kidney Injury Guidelines
- European Association for Study of Liver Guidelines
- American Diabetes Association Standards
- WHO Hematology Guidelines

*Note: In production, integrate with a vector database (Pinecone, Weaviate) for comprehensive medical literature search.*

## 🔧 Configuration

### Biomarker Ranges

Edit `mediguard/data/biomarkers.json` to customize:
- Normal ranges
- Critical thresholds
- Units of measurement
- Category groupings

### Disease Prediction Rules

Edit `mediguard/models/predictor.py` to adjust:
- Clinical criteria
- Probability weights
- Biomarker relevance mappings

*For ML model integration: Replace rule-based logic with trained classifier (sklearn, TensorFlow, PyTorch)*

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Twilio](https://www.twilio.com/) for WhatsApp API
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- Medical literature databases (PubMed, Cochrane)
- Healthcare professionals who validated clinical criteria

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues)
- 📧 **Contact**: Via GitHub or WhatsApp bot

## ⚠️ Important Notes

1. **Not FDA Approved**: This is research/educational software
2. **Requires Validation**: All predictions must be clinically validated
3. **Continuous Monitoring**: System should be monitored for accuracy
4. **Regional Variations**: Adjust reference ranges for your population
5. **Regular Updates**: Keep medical knowledge base current

## 🔮 Roadmap

- [ ] ML model training on clinical datasets
- [ ] Multi-language support
- [ ] Voice note input support
- [ ] PDF lab report parsing (OCR)
- [ ] Integration with EHR systems
- [ ] Real-time vital signs monitoring
- [ ] Trend analysis over time
- [ ] Clinical decision support algorithms
- [ ] Telemedicine integration

---

<p align="center">
  Made with ❤️ for Healthcare by <a href="https://github.com/N1KH1LT0X1N">N1KH1LT0X1N</a>
</p>

<p align="center">
  ⚕️ Improving clinical triage through AI ⚕️
</p>

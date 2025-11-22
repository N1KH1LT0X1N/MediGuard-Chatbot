# 🤖 WhatsApp AI Bots Collection

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> A collection of AI-powered WhatsApp bots for research and healthcare

This repository contains two powerful WhatsApp bots built with Flask and Google Gemini AI:

---

## 🏥 MediGuard AI - Clinical Triage System

<img src="https://img.shields.io/badge/Status-Production_Ready-brightgreen" alt="Production Ready"/>

**AI-powered clinical blood test analysis and disease prediction via WhatsApp.**

### Features
- 🔬 **24 Biomarker Analysis** - Comprehensive blood test evaluation
- 🎯 **Disease Prediction** - 9 disease categories with confidence scores
- 📚 **Medical References** - Evidence-based citations
- 🔒 **HIPAA-Compliant** - Secure, anonymized logging
- ⚡ **Real-time Analysis** - Instant predictions via WhatsApp

### Quick Links
- 📖 **[Full Documentation](README_MEDIGUARD.md)**
- 💬 **[Sample Conversations](SAMPLE_CONVERSATIONS.md)**
- 🚀 **[Complete Setup Guide](COMPLETE_SETUP.md#mediguard-ai-setup)**

### Quick Start
```bash
# Run MediGuard AI Bot
python mediguard_bot.py

# Or run the REST API
python api/predict_api.py
```

### Supported Biomarkers (24)
Hemoglobin, WBC, Platelets, Glucose, Creatinine, BUN, Electrolytes (Na, K, Cl, Ca), Liver Enzymes (ALT, AST, Bilirubin, Albumin, Total Protein), Cardiac Markers (LDH, Troponin, BNP), Inflammation (CRP, ESR, Procalcitonin), Coagulation (D-Dimer, INR), Lactate

### Disease Categories (9)
Sepsis, Acute Cardiac Event, Acute Renal Failure, Liver Disease, Metabolic Disorder, Coagulopathy, Anemia, Infection, Normal Range

---

## 📚 Research Paper Chatbot

<img src="https://img.shields.io/badge/Status-Active-blue" alt="Active"/>

**AI-powered research paper search, summarization, and Q&A via WhatsApp.**

### Features
- 🔍 **Smart Paper Search** - Search Semantic Scholar and arXiv
- 📝 **Structured Summaries** - Auto-generated paper summaries
- 💬 **Interactive Q&A** - Test understanding with AI questions
- 🎯 **Intent Detection** - Smart command parsing
- 📊 **Progress Tracking** - Score Q&A performance

### Quick Links
- 📖 **[Full Documentation](research-paper-bot/README.md)**
- 🌐 **[Live Demo](https://research-paper-chatbot-2.onrender.com)**
- 🚀 **[Complete Setup Guide](COMPLETE_SETUP.md#research-paper-bot-setup)**

### Quick Start
```bash
# Run Research Paper Bot
python research-paper-bot/research_bot.py
```

### WhatsApp Commands
```
transformer attention       # Search papers
select 1                   # Choose a paper
start qna                  # Begin Q&A
more details intro         # Get section details
help                       # Show commands
```

---

## 🚀 Quick Start (Both Bots)

### 1. Clone & Install
```bash
git clone https://github.com/N1KH1LT0X1N/Whatsapp-Bot.git
cd Whatsapp-Bot
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Choose Your Bot
```bash
# MediGuard AI (Port 5000)
python mediguard_bot.py

# OR Research Paper Bot (Port 5000)
python research-paper-bot/research_bot.py
```

### 4. Expose with ngrok
```bash
ngrok http 5000
```

### 5. Configure Twilio
Set webhook to: `https://your-ngrok-url.ngrok.io/whatsapp`

---

## 📋 Requirements

### Common Requirements
- Python 3.9+
- Twilio WhatsApp account
- Google Gemini API key
- Flask web server

### Additional for MediGuard AI
- NumPy, scikit-learn (for ML models)
- Enhanced security logging

---

## 📁 Repository Structure

```
Whatsapp-Bot/
├── mediguard_bot.py                 # 🏥 MediGuard AI bot (main)
├── mediguard/                       # MediGuard package
│   ├── models/                      # Prediction & scaling
│   ├── parsers/                     # Input parsing
│   ├── knowledge/                   # RAG engine
│   ├── utils/                       # Security & formatters
│   └── data/                        # Biomarker metadata
├── api/                             # REST API
│   └── predict_api.py               # Prediction endpoint
├── research-paper-bot/              # 📚 Research bot
│   ├── research_bot.py              # Main bot
│   ├── README.md                    # Documentation
│   └── tests/                       # Test suite
├── tests/                           # MediGuard tests
│   └── test_mediguard.py
├── README.md                        # This file
├── README_MEDIGUARD.md              # MediGuard docs
├── SAMPLE_CONVERSATIONS.md          # Example interactions
├── COMPLETE_SETUP.md                # Comprehensive setup guide
├── .env.example                     # Environment template
├── requirements.txt                 # Dependencies
├── requirements-dev.txt             # Dev dependencies
├── wsgi.py                          # WSGI entry point
├── Procfile                         # Deployment config
├── LICENSE                          # Apache 2.0
├── SECURITY.md                      # Security policy
├── CONTRIBUTING.md                  # Contribution guide
└── CODE_OF_CONDUCT.md               # Code of conduct
```

---

## 🏗️ Architecture

### MediGuard AI Flow
```
WhatsApp → Twilio → mediguard_bot.py
                        ↓
                  Input Parser → JSON/CSV/Key-Value
                        ↓
                  Biomarker Scaler → Normalize values
                        ↓
                  Predictor → Disease classification
                        ↓
                  RAG Engine → Medical references
                        ↓
                  Formatter → WhatsApp response
                        ↓
                  Secure Logger → Anonymized audit
```

### Research Bot Flow
```
WhatsApp → Twilio → research_bot.py
                        ↓
                  Intent Detection → Command parsing
                        ↓
                  Session Manager → User state
                        ↓
                  Paper Search → Semantic Scholar/arXiv
                        ↓
                  Gemini AI → Summaries & Q&A
                        ↓
                  Formatter → WhatsApp response
```

---

## 🧪 Testing

### Test MediGuard AI
```bash
pytest tests/test_mediguard.py -v
```

### Test Research Bot
```bash
pytest research-paper-bot/tests/ -v
```

### Run All Tests
```bash
pytest -v
```

### With Coverage
```bash
pytest --cov=mediguard --cov=research-paper-bot --cov-report=html
```

---

## 🌐 Deployment

### Deploy MediGuard AI
```bash
# Using Gunicorn
gunicorn mediguard_bot:app

# Using Docker
docker build -t mediguard-ai .
docker run -p 5000:5000 --env-file .env mediguard-ai
```

### Deploy Research Bot
```bash
# Update wsgi.py to use research_bot
# Then deploy normally
gunicorn wsgi:app
```

### Cloud Platforms
Both bots support:
- ✅ Render.com
- ✅ Heroku
- ✅ AWS (EC2, ECS)
- ✅ Google Cloud Run
- ✅ Azure App Service

See [COMPLETE_SETUP.md](COMPLETE_SETUP.md) for detailed deployment instructions.

---

## 🔒 Security

Both bots implement:
- ✅ User anonymization
- ✅ Input validation (SQL/XSS injection prevention)
- ✅ Secure logging
- ✅ Data retention policies
- ✅ HTTPS required in production

### MediGuard AI Additional Security
- HIPAA-compliant logging
- PHI removal from logs
- Anonymized session tracking
- Audit trail

See [SECURITY.md](SECURITY.md) for details.

---

## 📊 Comparison

| Feature | MediGuard AI | Research Bot |
|---------|-------------|--------------|
| **Domain** | Healthcare / Clinical | Academic / Research |
| **Primary Use** | Blood test analysis | Paper search & learning |
| **Input Format** | JSON/CSV/Key-Value | Natural language |
| **AI Model** | Rule-based + ML | Google Gemini |
| **Output** | Disease prediction | Paper summaries |
| **Security** | HIPAA-compliant | Standard |
| **Validation** | Medical references | Citation tracking |
| **Target Users** | Clinicians, nurses | Researchers, students |
| **Deployment** | Production-ready | Active |

---

## 📖 Documentation

### Comprehensive Guides
- 🚀 **[Complete Setup Guide](COMPLETE_SETUP.md)** - Step-by-step for both bots
- 🏥 **[MediGuard Documentation](README_MEDIGUARD.md)** - Full MediGuard guide
- 📚 **[Research Bot Documentation](research-paper-bot/README.md)** - Research bot guide
- 💬 **[Sample Conversations](SAMPLE_CONVERSATIONS.md)** - Example interactions
- 🔒 **[Security Policy](SECURITY.md)** - Security guidelines
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

### API Documentation
- **MediGuard REST API**: See [README_MEDIGUARD.md#rest-api](README_MEDIGUARD.md#-rest-api)
- **Research Bot**: WebSocket-based via Twilio

---

## ⚠️ Important Disclaimers

### MediGuard AI
**CRITICAL:** MediGuard AI is for **educational and triage purposes only**. This system does NOT replace professional medical judgment or diagnosis. All predictions must be reviewed by qualified healthcare providers before making clinical decisions.

- ✅ Use for: Education, triage support, research
- ❌ NOT for: Primary diagnosis, treatment decisions, patient self-diagnosis

**Not FDA approved.** Requires clinical validation.

### Research Bot
For educational and research purposes. Always verify information from primary sources and consult original papers for critical research.

---

## 🤝 Contributing

We welcome contributions to both bots!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies
- [Google Gemini AI](https://ai.google.dev/) - Powerful AI capabilities
- [Twilio](https://www.twilio.com/) - WhatsApp API
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [NumPy](https://numpy.org/) & [scikit-learn](https://scikit-learn.org/) - ML libraries

### Data Sources
- [Semantic Scholar](https://www.semanticscholar.org/) - Academic paper search
- [arXiv](https://arxiv.org/) - Open-access research
- Medical literature databases (PubMed, Cochrane)
- Clinical guidelines (WHO, AHA, KDIGO, etc.)

---

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues)
- 💬 **Questions**: Open a discussion
- 📧 **Contact**: Via GitHub

---

## 🔮 Roadmap

### MediGuard AI
- [ ] Train ML models on clinical datasets
- [ ] PDF lab report OCR
- [ ] Multi-language support
- [ ] EHR integration
- [ ] Trend analysis over time
- [ ] Clinical decision support algorithms

### Research Bot
- [ ] Multi-document comparison
- [ ] Citation export (BibTeX, APA)
- [ ] Voice note support
- [ ] PDF upload and parsing
- [ ] Collaborative study sessions
- [ ] Spaced repetition learning

---

<p align="center">
  <strong>Made with ❤️ by <a href="https://github.com/N1KH1LT0X1N">N1KH1LT0X1N</a></strong>
</p>

<p align="center">
  <strong>🏥 Empowering Healthcare • 📚 Advancing Research • 🤖 Powered by AI</strong>
</p>

<p align="center">
  <a href="COMPLETE_SETUP.md">📖 Setup Guide</a> •
  <a href="README_MEDIGUARD.md">🏥 MediGuard Docs</a> •
  <a href="research-paper-bot/README.md">📚 Research Bot Docs</a> •
  <a href="https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues">🐛 Report Issues</a>
</p>

# 🚀 Complete Setup Guide - WhatsApp AI Bots

This comprehensive guide will walk you through setting up both the **MediGuard AI** and **Research Paper Bot** from scratch.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Common Setup Steps](#common-setup-steps)
3. [MediGuard AI Setup](#mediguard-ai-setup)
4. [Research Paper Bot Setup](#research-paper-bot-setup)
5. [Twilio WhatsApp Configuration](#twilio-whatsapp-configuration)
6. [Testing Your Bots](#testing-your-bots)
7. [Deployment Options](#deployment-options)
8. [Troubleshooting](#troubleshooting)
9. [Security Hardening](#security-hardening)
10. [FAQ](#faq)

---

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Python**: 3.9 or higher
- **RAM**: Minimum 2GB (4GB+ recommended for MediGuard AI)
- **Storage**: 500MB free space
- **Internet**: Stable connection for API calls

### Required Accounts
1. **Twilio Account** (Free tier available)
   - Sign up: https://www.twilio.com/try-twilio
   - WhatsApp Sandbox or approved number

2. **Google AI Studio** (Free tier available)
   - Sign up: https://ai.google.dev/
   - Create API key for Gemini

3. **GitHub Account** (For cloning and deployment)
   - Sign up: https://github.com/join

### Required Tools
```bash
# Check Python version
python --version  # Should be 3.9+

# Install pip (if not installed)
python -m ensurepip --upgrade

# Install virtualenv (recommended)
pip install virtualenv

# Install git
# Linux: sudo apt-get install git
# macOS: brew install git
# Windows: Download from git-scm.com

# Install ngrok (for local development)
# Download from: https://ngrok.com/download
```

---

## Common Setup Steps

These steps apply to both bots.

### 1. Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/N1KH1LT0X1N/Whatsapp-Bot.git
cd Whatsapp-Bot

# OR clone via SSH (if you have SSH keys set up)
git clone git@github.com:N1KH1LT0X1N/Whatsapp-Bot.git
cd Whatsapp-Bot
```

### 2. Create Virtual Environment

**Recommended for isolated dependencies:**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt

# Verify installation
pip list | grep -E "flask|twilio|google-generativeai"
```

### 4. Get API Keys

#### Twilio Setup
1. Go to https://console.twilio.com/
2. Sign up or log in
3. Navigate to: **Develop** → **Messaging** → **Settings** → **WhatsApp Sandbox**
4. Note down:
   - Account SID (starts with `AC...`)
   - Auth Token
   - WhatsApp Sandbox Number (e.g., `whatsapp:+14155238886`)

#### Google Gemini API
1. Go to https://ai.google.dev/
2. Click **Get API Key**
3. Create new project or select existing
4. Click **Create API Key**
5. Copy the API key (starts with `AIza...`)

### 5. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor: vim, code, etc.
```

**Edit `.env` with your credentials:**

```env
# ======================
# Twilio WhatsApp Configuration
# ======================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your actual SID
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Your Twilio WhatsApp number

# ======================
# Google Gemini AI
# ======================
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your actual API key
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.5

# ======================
# MediGuard AI Configuration (if using MediGuard)
# ======================
PORT=5000
ANONYMIZATION_SALT=change_this_to_random_string_in_production
LOG_RETENTION_DAYS=30
API_PORT=5001
API_HOST=0.0.0.0
ENVIRONMENT=development
```

**Generate secure ANONYMIZATION_SALT:**
```bash
# Linux/macOS
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Save and close the file** (Ctrl+O, Enter, Ctrl+X in nano)

---

## MediGuard AI Setup

MediGuard AI is a clinical triage system for blood test analysis.

### 1. Verify MediGuard Components

```bash
# Check that MediGuard files exist
ls -l mediguard_bot.py
ls -l mediguard/
ls -l api/predict_api.py
ls -l mediguard/data/biomarkers.json
```

### 2. Test MediGuard Installation

```bash
# Test import
python -c "from mediguard.models.predictor import MediGuardPredictor; print('✅ MediGuard imports working')"

# Run tests
pytest tests/test_mediguard.py -v

# Expected output: All tests should pass
```

### 3. Run MediGuard Bot

```bash
# Run the bot
python mediguard_bot.py

# Expected output:
# MediGuard AI Bot starting on port 5000...
#  * Running on http://0.0.0.0:5000
```

### 4. Test MediGuard Bot Locally

Open a new terminal (keep the bot running in the first terminal):

```bash
# Test root endpoint
curl http://localhost:5000/

# Expected: "MediGuard AI WhatsApp Bot is running. 🏥"

# Test health check
curl http://localhost:5000/health

# Expected: {"status": "healthy", "service": "mediguard-bot"}
```

### 5. (Optional) Run MediGuard REST API

If you want to use the standalone REST API:

```bash
# In a new terminal
python api/predict_api.py

# Runs on port 5001 by default
```

**Test the API:**
```bash
# Get biomarkers list
curl http://localhost:5001/api/biomarkers

# Test prediction (example with normal values)
curl -X POST http://localhost:5001/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "biomarkers": {
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
  }'
```

### 6. MediGuard Input Formats

MediGuard accepts three input formats:

**JSON Format:**
```json
{
  "hemoglobin": 14.5,
  "wbc_count": 7.2,
  ...
}
```

**Key-Value Format:**
```
hemoglobin=14.5, wbc_count=7.2, platelet_count=250, ...
```

**CSV Format (24 values in order):**
```
14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5
```

---

## Research Paper Bot Setup

Research Paper Bot helps search, summarize, and learn from academic papers.

### 1. Verify Research Bot Components

```bash
# Check that Research Bot files exist
ls -l research-paper-bot/research_bot.py
ls -l research-paper-bot/README.md
ls -l research-paper-bot/tests/
```

### 2. Test Research Bot Installation

```bash
# Run tests
pytest research-paper-bot/tests/ -v

# Expected output: All tests should pass
```

### 3. Run Research Bot

```bash
# Run the bot
python research-paper-bot/research_bot.py

# Expected output:
#  * Running on http://0.0.0.0:5000
```

### 4. Test Research Bot Locally

Open a new terminal:

```bash
# Test root endpoint
curl http://localhost:5000/

# Expected: "Research Paper WhatsApp Bot is running."
```

### 5. Research Bot Commands

Available WhatsApp commands:
- `transformer attention` - Search papers
- `select 1` - Choose a paper
- `start qna` - Begin Q&A
- `more details intro` - Get section details
- `skip` / `repeat` - During Q&A
- `help` - Show commands
- `status` - Check session
- `reset` - Clear session

---

## Twilio WhatsApp Configuration

This section applies to both bots. You can only run one bot at a time on the same Twilio number.

### 1. Expose Local Server with ngrok

While your bot is running:

```bash
# In a new terminal, run ngrok
ngrok http 5000

# Expected output:
# Forwarding  https://abcd1234.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abcd1234.ngrok.io`)

**Important:**
- Keep ngrok running while testing
- URL changes each time you restart ngrok (free tier)
- For permanent URL, use ngrok paid plan or deploy to cloud

### 2. Configure Twilio Webhook

1. Go to https://console.twilio.com/
2. Navigate to: **Develop** → **Messaging** → **Settings** → **WhatsApp Sandbox**
3. Find: **"When a message comes in"**
4. Enter your webhook URL:
   ```
   https://your-ngrok-url.ngrok.io/whatsapp
   ```
   **Example:** `https://abcd1234.ngrok.io/whatsapp`
5. **Method:** POST
6. Click **Save**

### 3. Join WhatsApp Sandbox

1. In Twilio Console, find your **Sandbox Join Code**
   - Example: `join pocket-afternoon`
2. Send this message to your Twilio WhatsApp number
   - Send to: The number shown (e.g., +1 415 523 8886)
   - Message: `join pocket-afternoon`
3. You should receive a confirmation message

### 4. Test WhatsApp Integration

#### For MediGuard AI:
Send to your Twilio WhatsApp number:
```
/start
```

Expected response:
```
Welcome to MediGuard AI! 🏥
I'm your clinical triage assistant...
```

#### For Research Bot:
Send:
```
hello
```

Expected response:
```
I help you find and learn research papers...
```

---

## Testing Your Bots

### MediGuard AI Tests

#### Test 1: Help Command
```
Message: help
Expected: Help message with instructions
```

#### Test 2: Template Request
```
Message: template
Expected: JSON template with all 24 biomarkers
```

#### Test 3: Normal Lab Results
```json
Message: {
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

Expected: Prediction of "Normal Range" with high confidence
```

#### Test 4: Follow-up Commands
```
Message: explain more
Expected: Detailed analysis

Message: show sources
Expected: Medical references
```

### Research Bot Tests

#### Test 1: Paper Search
```
Message: attention is all you need
Expected: List of papers with "select 1" instruction
```

#### Test 2: Paper Selection
```
Message: select 1
Expected: Structured summary with Introduction, Methodology, Results, Conclusions
```

#### Test 3: Q&A
```
Message: start qna
Expected: First question about the paper
```

#### Test 4: Utility Commands
```
Message: help
Expected: List of commands

Message: status
Expected: Current session status

Message: reset
Expected: Session cleared confirmation
```

---

## Deployment Options

### Option 1: Render (Recommended)

**Free tier available, automatic HTTPS**

1. **Create Account**
   - Sign up at https://render.com
   - Connect your GitHub account

2. **Create New Web Service**
   - Click **New** → **Web Service**
   - Connect repository: `N1KH1LT0X1N/Whatsapp-Bot`
   - **Name:** `mediguard-ai` or `research-paper-bot`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:**
     - MediGuard: `gunicorn mediguard_bot:app`
     - Research Bot: `gunicorn research-paper-bot.research_bot:app`

3. **Add Environment Variables**
   - In Render dashboard, go to **Environment**
   - Add all variables from your `.env` file
   - Click **Save Changes**

4. **Deploy**
   - Click **Create Web Service**
   - Wait for deployment (5-10 minutes)
   - Copy your Render URL (e.g., `https://mediguard-ai.onrender.com`)

5. **Update Twilio Webhook**
   - Go to Twilio Console
   - Update webhook URL to:
     ```
     https://your-app-name.onrender.com/whatsapp
     ```

### Option 2: Heroku

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create mediguard-ai

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=ACxxx...
heroku config:set TWILIO_AUTH_TOKEN=xxx...
heroku config:set GEMINI_API_KEY=xxx...
heroku config:set ANONYMIZATION_SALT=xxx...

# Deploy
git push heroku main

# Check logs
heroku logs --tail

# Open app
heroku open
```

### Option 3: Docker

**Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# For MediGuard
CMD ["gunicorn", "-b", "0.0.0.0:5000", "mediguard_bot:app"]

# OR for Research Bot
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "research-paper-bot.research_bot:app"]
```

**Build and run:**
```bash
# Build image
docker build -t mediguard-ai .

# Run container
docker run -p 5000:5000 --env-file .env mediguard-ai

# Or with docker-compose
docker-compose up
```

### Option 4: AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# 4. Clone repository
git clone https://github.com/N1KH1LT0X1N/Whatsapp-Bot.git
cd Whatsapp-Bot

# 5. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Create .env file with your credentials
nano .env

# 7. Run with supervisor or systemd
sudo nano /etc/systemd/system/mediguard.service
```

**systemd service file:**
```ini
[Unit]
Description=MediGuard AI Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Whatsapp-Bot
Environment="PATH=/home/ubuntu/Whatsapp-Bot/venv/bin"
ExecStart=/home/ubuntu/Whatsapp-Bot/venv/bin/gunicorn -b 0.0.0.0:5000 mediguard_bot:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable mediguard
sudo systemctl start mediguard
sudo systemctl status mediguard
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Bot doesn't respond on WhatsApp

**Symptoms:** Messages sent, but no response

**Solutions:**
1. Check bot is running:
   ```bash
   curl http://localhost:5000/
   ```
2. Verify ngrok is running and URL is correct
3. Check Twilio webhook URL ends with `/whatsapp`
4. View bot logs for errors
5. Check Twilio Console → Monitor → Logs for webhook failures

#### Issue 2: "Missing required environment variables"

**Symptoms:** Bot crashes on startup

**Solutions:**
1. Verify `.env` file exists:
   ```bash
   ls -la .env
   ```
2. Check all required variables are set:
   ```bash
   cat .env | grep -E "TWILIO|GEMINI"
   ```
3. No extra spaces or quotes in .env:
   ```env
   # ✅ Correct
   TWILIO_ACCOUNT_SID=ACxxxxx

   # ❌ Wrong
   TWILIO_ACCOUNT_SID = "ACxxxxx"
   ```
4. Restart bot after updating .env

#### Issue 3: Module not found errors

**Symptoms:** `ImportError` or `ModuleNotFoundError`

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify installation
pip list

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue 4: Database errors

**Symptoms:** SQLite locked or permission errors

**Solutions:**
```bash
# Check database permissions
ls -l *.db

# Remove old database (will be recreated)
rm mediguard.db whatsapp_bot.db

# Restart bot
```

#### Issue 5: API rate limits

**Symptoms:** "Rate limit exceeded" errors

**Solutions:**
1. **Twilio:** Wait a few minutes, implement rate limiting
2. **Gemini:** Check quota at https://ai.google.dev/
3. **Semantic Scholar:** Built-in fallback to arXiv

#### Issue 6: MediGuard prediction errors

**Symptoms:** "Error processing prediction"

**Solutions:**
1. Check input format matches one of: JSON, CSV, or key-value
2. Verify all 24 biomarkers are provided
3. Check values are numeric
4. View logs for specific error:
   ```bash
   tail -f /path/to/logs
   ```

#### Issue 7: Research Bot no search results

**Symptoms:** "I couldn't find any papers"

**Solutions:**
1. Check internet connectivity
2. Try simpler search terms
3. Semantic Scholar API may be down (automatic fallback to arXiv)
4. Check bot logs for API errors

### Debug Mode

Enable debug logging:

```python
# In mediguard_bot.py or research_bot.py
# Change last line to:
app.run(host="0.0.0.0", port=port, debug=True)
```

**Warning:** Never use `debug=True` in production!

### Check Logs

```bash
# Flask console logs (running bot)
python mediguard_bot.py 2>&1 | tee bot.log

# Twilio logs
# Go to https://console.twilio.com/ → Monitor → Logs

# ngrok logs
# In ngrok dashboard: http://127.0.0.1:4040
```

---

## Security Hardening

### Production Checklist

#### 1. Environment Variables
```bash
# ✅ Generate strong ANONYMIZATION_SALT
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ✅ Use production Gemini API key
# ✅ Enable Twilio webhook signature validation
# ✅ Never commit .env to git
```

#### 2. HTTPS Only
```bash
# ✅ Use HTTPS in production (Render provides automatically)
# ✅ Set up nginx reverse proxy if self-hosting
# ✅ Configure SSL certificates (Let's Encrypt)
```

#### 3. Database Security
```bash
# ✅ Set restrictive permissions
chmod 600 mediguard.db

# ✅ Use PostgreSQL in production
# ✅ Enable automated backups
```

#### 4. Rate Limiting

Add to your bot:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

#### 5. Logging

```bash
# ✅ Enable secure logging
# ✅ Set up log rotation
# ✅ Monitor for suspicious activity
# ✅ Implement data retention policies
```

#### 6. MediGuard Specific

```bash
# ✅ Verify anonymization is working
python -c "from mediguard.utils.security import anonymize_user_id; print(anonymize_user_id('test'))"

# ✅ Test PHI removal from logs
# ✅ Set up HIPAA-compliant backup storage
# ✅ Implement audit trail monitoring
```

---

## FAQ

### General Questions

**Q: Can I run both bots at the same time?**
A: Yes, but they need different ports. Run MediGuard on 5000 and Research Bot on 5001, then use different Twilio numbers for each.

**Q: Do I need to pay for Twilio/Gemini?**
A: Both have free tiers sufficient for development. Twilio Sandbox is free, Gemini has generous free quota.

**Q: Can I use this commercially?**
A: Check the Apache 2.0 license. For MediGuard AI, note it's NOT FDA approved and requires clinical validation.

**Q: How do I update the bots?**
A: `git pull origin main` then restart the bot.

### MediGuard Questions

**Q: Is MediGuard FDA approved?**
A: No. It's for educational/triage purposes only. All predictions must be reviewed by healthcare professionals.

**Q: Can I add more biomarkers?**
A: Yes! Edit `mediguard/data/biomarkers.json` and update the parser.

**Q: How accurate are the predictions?**
A: Current implementation uses rule-based clinical criteria. For production, train ML models on validated datasets.

**Q: Can I integrate with EHR systems?**
A: Yes, use the REST API endpoint (`/api/predict`) for integration.

### Research Bot Questions

**Q: Why no search results?**
A: Check API limits or try simpler terms. Bot automatically falls back to arXiv.

**Q: Can I search for specific authors?**
A: Yes, include author name in search: "attention vaswani"

**Q: How are summaries generated?**
A: Using Google Gemini AI based on paper abstracts.

---

## Next Steps

### For Development
1. ✅ Set up pre-commit hooks (black, flake8)
2. ✅ Write additional tests
3. ✅ Configure CI/CD (GitHub Actions)
4. ✅ Set up monitoring (Sentry, Datadog)

### For Production
1. ✅ Deploy to cloud platform
2. ✅ Set up PostgreSQL database
3. ✅ Configure load balancer
4. ✅ Implement rate limiting
5. ✅ Set up monitoring and alerts
6. ✅ Enable automated backups
7. ✅ Configure log aggregation
8. ✅ Obtain security certifications (for MediGuard)

### For MediGuard AI
1. ✅ Train ML models on clinical datasets
2. ✅ Expand knowledge base
3. ✅ Add PDF lab report parsing (OCR)
4. ✅ Implement trend analysis
5. ✅ Clinical validation studies

### For Research Bot
1. ✅ Add citation export
2. ✅ Implement voice note support
3. ✅ PDF upload and parsing
4. ✅ Multi-document comparison

---

## Additional Resources

### Documentation
- [Main README](README.md)
- [MediGuard Documentation](README_MEDIGUARD.md)
- [Research Bot Documentation](research-paper-bot/README.md)
- [Sample Conversations](SAMPLE_CONVERSATIONS.md)
- [Security Policy](SECURITY.md)
- [Contributing Guide](CONTRIBUTING.md)

### External Links
- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [ngrok Documentation](https://ngrok.com/docs)

### Community
- [GitHub Issues](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues)
- [GitHub Discussions](https://github.com/N1KH1LT0X1N/Whatsapp-Bot/discussions)

---

<p align="center">
  <strong>🎉 Congratulations! You're all set up! 🎉</strong>
</p>

<p align="center">
  Need help? <a href="https://github.com/N1KH1LT0X1N/Whatsapp-Bot/issues">Open an issue</a>
</p>

<p align="center">
  <strong>Made with ❤️ by <a href="https://github.com/N1KH1LT0X1N">N1KH1LT0X1N</a></strong>
</p>

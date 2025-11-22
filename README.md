# 📚 Research-Paper-Chatbot

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> AI-powered WhatsApp bot for research paper search, Q&A, and structured summaries via Google Gemini.

Lightweight Flask-based WhatsApp assistant that helps you discover, understand, and learn from research papers through conversational AI. Search papers from Semantic Scholar and arXiv, get structured summaries, and test your understanding with interactive Q&A.

## 🚀 Live Demo

- **Deployed App**: https://research-paper-chatbot-2.onrender.com
- **Try it on WhatsApp**: https://wa.me/14155238886?text=join%20pocket-afternoon

## ✨ Features

- 🔍 **Smart Paper Search** - Search across Semantic Scholar and arXiv APIs
- 📝 **Structured Summaries** - Auto-generated summaries with Introduction, Methodology, Results, and Conclusions
- 💬 **Interactive Q&A** - Test your understanding with AI-generated questions
- 📱 **WhatsApp Integration** - Natural conversation interface via Twilio
- 🤖 **Google Gemini AI** - Powered by Gemini 2.5 Flash for intelligent responses
- 💾 **Session Management** - SQLite-based conversation tracking
- 🎯 **Intent Detection** - Smart command parsing and context awareness
- 📊 **Progress Tracking** - Score your Q&A performance

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask
- **AI**: Google Generative AI (Gemini 2.5 Flash)
- **Messaging**: Twilio WhatsApp API
- **Database**: SQLite
- **APIs**: Semantic Scholar Graph API, arXiv API
- **Deployment**: Render (WSGI with Gunicorn)

## 📋 Requirements

- Python 3.9+
- Twilio account (WhatsApp sandbox or approved number)
- Gemini API key (Generative AI API)

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot.git
cd Research-Paper-Chatbot
```

### 2️⃣ Set Up Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.5
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing tools):
```bash
pip install -r requirements-dev.txt
```

### 4️⃣ Run Locally

```bash
python research_bot.py
```

The app will start on `http://localhost:5000`

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

## 🎯 How to Use

### 📱 WhatsApp Commands

Send messages to your connected WhatsApp number:

**Search for Papers:**
```
transformer attention
attention is all you need
https://arxiv.org/abs/1706.03762
10.48550/arXiv.1706.03762
```

**Select a Paper:**
```
select 1
choose 2
pick 3
```

**Get Detailed Sections:**
```
more details intro
more details methodology
more details results
more details conclusions
```

**Start Interactive Q&A:**
```
start qna
ready for Q&A
let's do Q&A
```

**During Q&A:**
```
skip          # Skip current question
repeat        # Repeat current question
[your answer] # Answer the question
```

**Utility Commands:**
```
help          # Show available commands
status        # Check your current session
reset         # Clear session and start over
capabilities  # See what the bot can do
```

## 📊 Example Conversation

```
You: transformer attention
Bot: Here are the top results:
     1. Attention Is All You Need (2017) - Vaswani et al.
     ...
     Reply 'select 1' (or 2/3) to choose a paper.

You: select 1
Bot: [Structured summary with Introduction, Methodology, Results, Conclusions]
     What's next: start qna | more details intro|method|results|conclusions

You: start qna
Bot: Q&A started!
     Q1: What is the main innovation introduced in this paper?

You: self-attention mechanism
Bot: Great! You covered key points.
     Q2: ...
```

## 🏗️ Architecture

```
┌─────────────┐
│   WhatsApp  │
│    User     │
└──────┬──────┘
       │ Twilio WhatsApp API
       ▼
┌─────────────────────────────────┐
│      Flask Application          │
│  ┌──────────────────────────┐  │
│  │   /whatsapp endpoint     │  │
│  └────────┬─────────────────┘  │
│           │                     │
│  ┌────────▼─────────────────┐  │
│  │  Intent Detection        │  │
│  │  (browsing/qna/commands) │  │
│  └────────┬─────────────────┘  │
│           │                     │
│  ┌────────▼─────────────────┐  │
│  │  Session Manager         │  │
│  │  (SQLite DB)             │  │
│  └────────┬─────────────────┘  │
│           │                     │
│  ┌────────▼─────────────────┐  │
│  │  Paper Search            │  │
│  │  - Semantic Scholar API  │  │
│  │  - arXiv API             │  │
│  └────────┬─────────────────┘  │
│           │                     │
│  ┌────────▼─────────────────┐  │
│  │  AI Processing           │  │
│  │  - Summary Generation    │  │
│  │  - Q&A Generation        │  │
│  │  - Answer Evaluation     │  │
│  │  (Google Gemini)         │  │
│  └────────┬─────────────────┘  │
│           │                     │
│  ┌────────▼─────────────────┐  │
│  │  Response Formatter      │  │
│  │  (WhatsApp chunking)     │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

## 💾 Database Schema

**sessions table:**
- `user_id` (TEXT, PRIMARY KEY) - WhatsApp phone number
- `mode` (TEXT) - 'browsing' or 'qna'
- `selected_paper_id` (TEXT) - Current paper ID
- `selected_paper_title` (TEXT)
- `selected_paper_abstract` (TEXT)
- `qna_active` (INTEGER) - Q&A session flag
- `qna_index` (INTEGER) - Current question index
- `qna_questions` (TEXT) - JSON array of questions
- `score` (INTEGER) - User's Q&A score
- `last_results` (TEXT) - JSON array of search results
- `updated_at` (TEXT)

**logs table:**
- `id` (INTEGER, PRIMARY KEY)
- `user_id` (TEXT)
- `role` (TEXT) - 'user' or 'bot'
- `message` (TEXT)
- `created_at` (TEXT)

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=research_bot --cov-report=html
```

## 🔧 Troubleshooting

### Common Issues

**Problem: Bot doesn't respond to WhatsApp messages**
- ✅ Check ngrok is running and URL is updated in Twilio Console
- ✅ Verify webhook URL ends with `/whatsapp`
- ✅ Check Flask app is running without errors
- ✅ Verify Twilio credentials in `.env`

**Problem: "Missing required environment variables" error**
- ✅ Ensure `.env` file exists in project root
- ✅ Check all required variables are set: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `GEMINI_API_KEY`
- ✅ Restart the Flask app after updating `.env`

**Problem: Search returns no results**
- ✅ Check internet connectivity
- ✅ Semantic Scholar API may be rate-limited (fallback to arXiv automatically)
- ✅ Try simpler search terms

**Problem: AI summaries not generating**
- ✅ Verify `GEMINI_API_KEY` is valid
- ✅ Check Google AI Studio quota/limits
- ✅ Bot falls back to basic summaries if AI unavailable

**Problem: WhatsApp messages are truncated**
- ✅ Messages are automatically chunked to 1500 chars max
- ✅ Multi-part messages are tagged with (1/2), (2/2), etc.

**Problem: Database locked errors**
- ✅ SQLite DB is single-write; ensure only one Flask instance is running
- ✅ For production, consider PostgreSQL

### Debugging Tips

1. **Check logs**: Flask prints all requests/errors to console
2. **Test endpoints**: Visit `http://localhost:5000/` to verify server is up
3. **Twilio Console**: Check request logs in Twilio → Monitor → Logs
4. **Validate .env**: Ensure no extra spaces or quotes around values

## 🌐 Deployment

### Deploy to Render

1. Fork/clone this repository
2. Sign up at [Render.com](https://render.com)
3. Create a new **Web Service**
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
6. Add environment variables in Render Dashboard
7. Deploy!

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set TWILIO_ACCOUNT_SID=ACxxx...
heroku config:set TWILIO_AUTH_TOKEN=xxx...
heroku config:set GEMINI_API_KEY=xxx...
git push heroku main
```

## 📁 Project Structure

```
Research-Paper-Chatbot/
├── research_bot.py          # Main Flask application
├── wsgi.py                  # WSGI entry point
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── LICENSE                  # Apache 2.0 License
├── README.md                # This file
├── CONTRIBUTING.md          # Contribution guidelines
├── CODE_OF_CONDUCT.md       # Code of conduct
├── SECURITY.md              # Security policy
├── Procfile                 # Deployment config
├── runtime.txt              # Python version
├── whatsapp_bot.db          # SQLite database (auto-generated)
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_bot_logic.py
│   ├── test_api.py
│   └── test_search.py
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for powerful AI capabilities
- [Twilio](https://www.twilio.com/) for WhatsApp API
- [Semantic Scholar](https://www.semanticscholar.org/) for academic paper search
- [arXiv](https://arxiv.org/) for open-access research papers

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot/issues)
- 💬 **Questions**: Open a discussion or contact via WhatsApp

## 🔮 Future Enhancements

- [ ] Multi-document comparison
- [ ] Citation formatting and export
- [ ] Voice note support
- [ ] Image/diagram extraction from papers
- [ ] Collaborative study sessions
- [ ] PDF upload and parsing
- [ ] Custom Q&A difficulty levels
- [ ] Spaced repetition learning

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/N1KH1LT0X1N">N1KH1LT0X1N</a>
</p>

<p align="center">
  <a href="https://research-paper-chatbot-2.onrender.com">🌐 Live Demo</a> •
  <a href="https://wa.me/14155238886?text=join%20pocket-afternoon">💬 Try on WhatsApp</a> •
  <a href="https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot/issues">🐛 Report Bug</a>
</p>


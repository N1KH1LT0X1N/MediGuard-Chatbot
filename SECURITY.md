# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Research-Paper-Chatbot seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed
- Exploit the vulnerability for any purpose other than verification

### Please DO:

1. **Report via GitHub Security Advisories**
   - Go to the [Security tab](https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot/security/advisories) of this repository
   - Click "Report a vulnerability"
   - Provide detailed information about the vulnerability

2. **Include in your report:**
   - Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
   - Full paths of affected source file(s)
   - Location of the affected code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability
   - Any potential mitigations you've identified

### What to expect:

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will provide regular updates on our progress (at least every 5 business days)
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Credit**: If you wish, we will credit you in our security advisory and release notes

### Disclosure Policy

- Security issues are initially handled privately
- We will coordinate public disclosure after a fix is available
- We follow coordinated disclosure principles
- You will be notified when we plan to disclose the issue

## Security Best Practices for Users

### API Keys and Secrets

- **Never commit `.env` files** to version control
- **Use strong, unique API keys** for all services (Twilio, Google Gemini)
- **Rotate keys regularly** (at least every 90 days)
- **Use environment variables** for all sensitive configuration
- **Limit API key permissions** to only what's necessary

### Deployment Security

- **Use HTTPS** for all production deployments (Render provides this by default)
- **Enable Twilio webhook signature verification** (see code comments in `research_bot.py`)
- **Set restrictive CORS policies** if exposing additional API endpoints
- **Use a production-grade database** (PostgreSQL) instead of SQLite for production
- **Enable rate limiting** to prevent abuse
- **Monitor logs** for suspicious activity

### Database Security

- **Never expose the SQLite database** file publicly
- **Sanitize user inputs** before database queries
- **Use parameterized queries** (already implemented)
- **Regularly backup** your database
- **Implement data retention policies** and delete old session data

### WhatsApp Integration

- **Verify Twilio requests** using webhook signature validation
- **Implement rate limiting** per user to prevent spam
- **Sanitize message content** before processing
- **Don't store sensitive user information** without consent
- **Comply with GDPR/CCPA** if applicable to your users

### Google Gemini API

- **Monitor API usage** to detect anomalies
- **Set usage quotas** to prevent unexpected costs
- **Use the minimum required permissions**
- **Don't send sensitive user data** to the AI model
- **Implement content filtering** for generated responses

## Known Security Considerations

### Current Implementation

1. **SQLite Database**: 
   - SQLite is suitable for development and small deployments
   - For production with concurrent users, consider PostgreSQL
   - Database file should not be world-readable

2. **Session Management**:
   - User sessions are identified by WhatsApp phone numbers
   - No additional authentication is implemented
   - Consider adding user verification for sensitive deployments

3. **Rate Limiting**:
   - Not currently implemented in the application
   - Rely on Twilio's built-in rate limiting
   - Consider adding application-level rate limiting for production

4. **Input Validation**:
   - Basic validation is implemented
   - Consider adding more robust input sanitization
   - Watch for injection attacks in user queries

5. **Logging**:
   - All user messages are logged to the database
   - Ensure compliance with privacy regulations
   - Implement log rotation and retention policies

## Security Updates

We regularly review our dependencies for known vulnerabilities. To update dependencies:

```bash
# Check for outdated packages
pip list --outdated

# Update a specific package
pip install --upgrade package-name

# Update requirements file
pip freeze > requirements.txt
```

## Automated Security Scanning

This project uses:
- **Dependabot** for dependency vulnerability alerts (enable in GitHub settings)
- **GitHub CodeQL** for code scanning (recommended)

To enable security features:
1. Go to repository Settings → Security & analysis
2. Enable Dependabot alerts and security updates
3. Enable Secret scanning

## Contact

For non-security-related issues, please use [GitHub Issues](https://github.com/N1KH1LT0X1N/Research-Paper-Chatbot/issues).

For urgent security matters that cannot be reported through GitHub, you may contact the maintainer through the repository's social channels.

---

**Last updated**: October 31, 2025

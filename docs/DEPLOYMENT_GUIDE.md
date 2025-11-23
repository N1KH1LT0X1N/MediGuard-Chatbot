# 🚀 Deploying MediGuard AI to Render

This guide will walk you through deploying your WhatsApp bot to Render.com.

## Prerequisites

1. **GitHub Account**: Your code must be pushed to a GitHub repository.
2. **Render Account**: Sign up at [render.com](https://render.com).
3. **Twilio Account**: You'll need your SID, Auth Token, and WhatsApp Sandbox settings.
4. **Gemini API Key**: For the AI features.

## Step 1: Prepare Your Repository

Ensure your repository has the following files (already checked and present):
- `requirements.txt`: Lists all dependencies (including `gunicorn`).
- `Procfile`: Tells Render how to run the app (`web: gunicorn wsgi:app`).
- `runtime.txt`: Specifies Python version (`python-3.11.0`).
- `wsgi.py`: Entry point for the application.

## Step 2: Create a Web Service on Render

1. Log in to your Render dashboard.
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select your `Whatsapp-Bot` repository.
4. **Name**: Give it a name (e.g., `mediguard-bot`).
5. **Region**: Choose the one closest to you (e.g., `Singapore` or `Frankfurt`).
6. **Branch**: `main` (or `master`).
7. **Root Directory**: Leave blank (defaults to root).
8. **Runtime**: `Python 3`.
9. **Build Command**: `pip install -r requirements.txt`.
10. **Start Command**: `gunicorn wsgi:app`.
11. **Plan**: Select **Free** (or a paid plan for better performance).

## Step 3: Configure Environment Variables

Scroll down to the **Environment Variables** section and add the following keys from your `.env` file:

| Key | Value |
|-----|-------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` (or your sender number) |
| `GEMINI_API_KEY` | Your Google Gemini API Key |
| `PYTHON_VERSION` | `3.11.0` (optional, but good to specify) |

**Note:** Do NOT upload your `.env` file or `.db` files. The database will be recreated (note that SQLite on Render's free tier is ephemeral and will reset on redeployments).

## Step 4: Deploy

1. Click **Create Web Service**.
2. Render will start building your app. This may take a few minutes.
3. Watch the logs. You should eventually see `Build successful` and `Deploying...`.
4. Once deployed, you will see a URL like `https://mediguard-bot.onrender.com`.

## Step 5: Update Twilio Webhook

1. Copy your new Render URL (e.g., `https://mediguard-bot.onrender.com`).
2. Go to your [Twilio Console](https://console.twilio.com/).
3. Navigate to **Messaging > Try it out > Send a WhatsApp message** (Sandbox settings).
4. Paste your Render URL followed by `/whatsapp` into the **"When a message comes in"** field.
   - Example: `https://mediguard-bot.onrender.com/whatsapp`
5. Ensure the method is set to **POST**.
6. Click **Save**.

## Step 6: Verify

1. Send a message (e.g., "Hi") to your WhatsApp sandbox number.
2. The bot should reply!

## Troubleshooting

- **Build Failed**: Check the logs. Ensure `requirements.txt` is correct.
- **Application Error**: Check the logs. Ensure all environment variables are set correctly.
- **Database Reset**: Remember that on the free tier, the SQLite database is lost when the app restarts. For persistent data, you'd need a managed database (PostgreSQL), but for testing, this is fine.

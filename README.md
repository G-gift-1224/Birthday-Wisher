# 🎂 Auto Birthday Wisher
Schedule a birthday wish (photo + template + song -> generated video) that is delivered automatically at an exact time via Telegram, WhatsApp Cloud API and Instagram Story. You receive a delivery status on Telegram.

## Tech
FastAPI, APScheduler, SQLite, Pillow, FFmpeg, Telegram Bot API, WhatsApp Cloud API, Instagram Graph API.

## Run locally (Windows: double-click run.bat, it opens Chrome automatically)
1. Install FFmpeg. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill in the keys you need (Telegram alone is enough to start).
3. Put royalty-free `.mp3` files in `songs/`.
4. `uvicorn app.main:app --reload` and open http://localhost:8000

## Deploy
Use the Dockerfile on Render, Railway or Fly.io (keep the instance always on). Set PUBLIC_URL to the deployed URL; Instagram needs a public video link.

## Limits
WhatsApp personal Status is not supported (no official API). WhatsApp Cloud API needs an approved template and an opted-in recipient. Instagram needs a Business/Creator account.

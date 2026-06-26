# Uzdaily AI Telegram Bot

A Telegram bot that fetches and summarizes news from [uzdaily.uz](https://uzdaily.uz) using Google Gemini AI.

## Stack

- **aiogram 3** — Telegram Bot framework
- **LangGraph + LangChain** — AI agent workflow
- **Google Gemini 2.5 Flash** — language model
- **httpx + BeautifulSoup** — RSS parsing

## Setup

```bash
git clone https://github.com/Quvonchbek21/telegram_ai_chatbot.git
cd telegram_ai_chatbot
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

Get your tokens: [BotFather](https://t.me/BotFather) · [Google AI Studio](https://aistudio.google.com)

## Run

```bash
python main.py
```

## Usage

Send any topic to the bot and it will return the latest matching news from uzdaily.uz:

```
economy
dollar rate
sports
world news
```

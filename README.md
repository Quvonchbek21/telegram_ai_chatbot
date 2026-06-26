# Uzdaily AI Telegram Bot

> An AI-powered Telegram bot that delivers real-time news from [uzdaily.uz](https://uzdaily.uz) based on natural language queries.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=flat&logo=telegram&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-green?style=flat)

---

## Overview

Users send any topic in plain text — the bot queries the uzdaily.uz RSS feed, filters relevant articles, and returns a structured summary powered by Gemini 2.5 Flash. The agent automatically routes between casual conversation and news retrieval without explicit commands.

## Features

- Natural language news search in Uzbek and Russian
- Topic-aware filtering: economy, sports, technology, world news, and more
- LangGraph-based agent with tool-calling for reliable routing
- Graceful fallback when RSS is unavailable

## Tech Stack

| Layer | Technology |
|---|---|
| Bot framework | aiogram 3 |
| AI model | Google Gemini 2.5 Flash |
| Agent orchestration | LangGraph + LangChain |
| HTTP client | httpx (async) |
| HTML/RSS parsing | BeautifulSoup4 + lxml |
| Config | python-dotenv |

## Getting Started

### Prerequisites

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com)

### Installation

```bash
git clone https://github.com/Quvonchbek21/telegram_ai_chatbot.git
cd telegram_ai_chatbot

python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### Run

```bash
python main.py
```

## Usage

| Input | What the bot does |
|---|---|
| `economy` | Fetches latest economy news |
| `dollar rate` | Searches for currency-related articles |
| `world news` | Retrieves international headlines |
| `Hello!` | Responds conversationally without querying news |

## Project Structure

```
├── main.py          # Bot entry point, message handlers
├── agent.py         # LangGraph agent + Gemini integration
├── scraper.py       # RSS fetcher and HTML parser
├── requirements.txt
├── .env.example
└── .gitignore
```

## License

MIT

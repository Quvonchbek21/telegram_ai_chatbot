# Uzdaily AI Telegram Bot

Uzdaily.uz saytidan sun'iy intellekt yordamida yangilik qidirib beruvchi Telegram bot.

## Imkoniyatlari

- Uzdaily.uz RSS lentasidan so'nggi yangiliklar
- Mavzu bo'yicha qidirish: iqtisodiyot, sport, texnologiya va boshqalar
- Dunyo yangiliklari ham qo'llab-quvvatlanadi
- Gemini 2.5 Flash model asosida aqlli javoblar
- LangGraph agent arxitekturasi

## Texnologiyalar

- **aiogram 3** — Telegram Bot API
- **LangGraph + LangChain** — agent workflow
- **Google Gemini 2.5 Flash** — AI model
- **httpx + BeautifulSoup** — web scraping
- **python-dotenv** — muhit o'zgaruvchilari

## O'rnatish

```bash
git clone https://github.com/Quvonchbek21/telegram_ai_chatbot.git
cd telegram_ai_chatbot

python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

## Sozlash

`.env.example` faylini `.env` ga nusxalang va tokenlarni kiriting:

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- **BOT_TOKEN** — [@BotFather](https://t.me/BotFather) orqali oling
- **GEMINI_API_KEY** — [Google AI Studio](https://aistudio.google.com) dan oling

## Ishga tushirish

```bash
python main.py
```

## Foydalanish

Botga istalgan mavzuni yozing:

```
iqtisodiyot
dollar kursi
sport yangiliklari
dunyoda nima gap?
```

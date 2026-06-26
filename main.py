import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

from agent import ask

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "Men Uzdaily.uz saytidan yangilik qidiraman.\n"
        "Menga istalgan mavzuni yozing! ✍️\n\n"
        "Misol: <i>iqtisodiyot</i>, <i>texnologiya</i>, <i>sport</i>",
        parse_mode="HTML",
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "🔍 Qanday yangiliklarga qiziqyapsiz — men Uzdaily.uz dan topib beraman.\n\n"
        "Misol: <b>O'zbekistonda bo'layotgan hodisalar</b>, <b>yangi qonun</b>, <b>futbol</b>",
        parse_mode="HTML",
    )


import logging # Agar fayl boshida yo'q bo'lsa qo'shib qo'ying

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_query(message: Message):
    loading = await message.answer("🔍 Qidirilmoqda...")
    try:
        answer = await ask(message.text)
        await loading.delete()
        
        # Formatlash muammosi bo'lmasligi uchun parse_mode="HTML" ni vaqtinchalik olib tashlaymiz
        await message.answer(answer, disable_web_page_preview=True)
        
    except Exception as e:
        await loading.delete()
        
        # ❗️ MANA SHU QATOR XATONI TERMINALGA CHIQARADI
        print(f"------------- ASOSIY XATOLIK -------------")
        print(repr(e))
        logging.error(f"Xato detali: {e}", exc_info=True)
        print(f"------------------------------------------")
        
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())

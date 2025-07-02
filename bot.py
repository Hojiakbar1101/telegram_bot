import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties  # ✅ Yangi

from config import BOT_TOKEN
from database.db import init_db
from handlers import (
    start, profile, match, admin, vip,
    views, like, matchmaker, settings
)
from tasks.vip_reminder import send_vip_reminders  # 🆕 VIP tugash eslatmasi

# 🔧 Bot va dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ✅ To‘g‘ri usul
)
dp = Dispatcher(storage=MemoryStorage())

# 🔗 Router’larni ulash
dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(match.router)
dp.include_router(admin.router)
dp.include_router(vip.router)
dp.include_router(views.router)
dp.include_router(like.router)
dp.include_router(matchmaker.router)
dp.include_router(settings.router)

# 📋 Bot komandalar menyusi
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="admin", description="Admin panel (faqat adminlar uchun)"),
        BotCommand(command="stats", description="Statistikani ko‘rish"),
        BotCommand(command="segment", description="Foydalanuvchilar segmenti"),
        BotCommand(command="growth", description="VIP o‘sish statistikasi"),
        BotCommand(command="chart", description="VIP grafigi"),
        BotCommand(command="export", description="CSV eksport"),
        BotCommand(command="live", description="Real vaqt monitoring"),
    ]
    await bot.set_my_commands(commands)

# 🚀 Bot ishga tushganda
async def on_startup():
    init_db()
    await set_commands(bot)
    asyncio.create_task(send_vip_reminders(bot))  # 🆕 VIP tugash eslatmasi

# ▶️ Botni ishga tushirish
async def main():
    await on_startup()
    print("🤖 Sirli Tanishuv bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

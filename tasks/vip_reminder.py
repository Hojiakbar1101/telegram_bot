from database.db import SessionLocal
from database.models import User
from datetime import datetime, timedelta
from aiogram import Bot
from sqlalchemy import func
import logging

async def send_vip_reminders(bot: Bot):
    db = SessionLocal()
    try:
        tomorrow = datetime.utcnow().date() + timedelta(days=1)

        users = db.query(User).filter(
            User.is_premium == True,
            User.vip_until != None,
            func.date(User.vip_until) == tomorrow
        ).all()

        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text="⏰ Diqqat! VIP obunangiz ertaga tugaydi. Uni uzaytirishni unutmang 💎"
                )
            except Exception as e:
                logging.warning(f"❗ Xabar yuborib bo‘lmadi (ID: {user.telegram_id}): {e}")

    except Exception as e:
        logging.error(f"❌ VIP eslatma xatoligi: {e}")
    finally:
        db.close()

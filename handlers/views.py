from aiogram import Router, types
from database.db import SessionLocal
from database.models import User
from database.views import View
from datetime import datetime

router = Router()

@router.message(lambda msg: msg.text.lower() == "kim meni ko‘rdi")
async def who_viewed_me(message: types.Message):
    db = SessionLocal()
    me = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    # VIP tekshiruvi
    if not me or not me.vip_until or me.vip_until < datetime.now():
        await message.answer("⛔ Bu funksiya faqat VIP foydalanuvchilar uchun.")
        db.close()
        return

    views = db.query(View).filter(View.viewed_id == me.id).order_by(View.timestamp.desc()).all()
    if not views:
        await message.answer("👀 Hozircha hech kim profilni ko‘rmagan.")
    else:
        await message.answer("👁 Sizni ko‘rganlar:")
        for view in views[:10]:  # faqat oxirgi 10 ta
            viewer = db.query(User).filter(User.id == view.viewer_id).first()
            if viewer:
                await message.answer(
                    f"👤 {viewer.name}, {viewer.age} yosh\n"
                    f"📍 {viewer.city}\n"
                    f"🕒 {view.timestamp.strftime('%Y-%m-%d %H:%M')}"
                )
    db.close()

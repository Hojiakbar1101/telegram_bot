from aiogram import Router, types
from database.db import SessionLocal
from database.models import User
from database.views import View 
from datetime import datetime

router = Router()

@router.message(lambda msg: msg.text.lower() == "moslarni topish")
async def match_users(message: types.Message):
    db = SessionLocal()
    me = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not me:
        await message.answer("Avval profil to‘ldiring: /start")
        db.close()
        return

    if me.vip_until and me.vip_until > datetime.now():
        me.is_premium = True
    else:
        me.is_premium = False
    db.commit()

    matches = db.query(User).filter(
        User.gender != me.gender,
        User.city == me.city,
        User.id != me.id,
        User.is_hidden == False 
    ).order_by(User.is_premium.desc()).all()

    if not matches:
        await message.answer("Afsuski, hozircha mos foydalanuvchi topilmadi.")
    else:
        for match in matches:
            view = View(viewer_id=me.id, viewed_id=match.id)
            db.add(view)
            db.commit()

            await message.answer(
                f"👤 {match.name}, {match.age} yosh\n"
                f"📍 {match.city}\n"
                f"🎯 Qiziqishlari: {match.interests}\n"
                f"{'💎 VIP foydalanuvchi' if match.is_premium else ''}"
            )

    db.close()

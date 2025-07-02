from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import SessionLocal
from database.models import User
from database.likes import Like
from datetime import datetime

router = Router()

def is_vip(user: User) -> bool:
    return user.vip_until and user.vip_until > datetime.now()

@router.message(lambda msg: msg.text.lower() == "moslarni topish")
async def show_match_with_buttons(message: types.Message):
    db = SessionLocal()
    me = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not me:
        await message.answer("Avval profil to‘ldiring: /start")
        db.close()
        return

    if not is_vip(me):
        await message.answer("⛔ Bu funksiya faqat VIP foydalanuvchilar uchun.")
        db.close()
        return

    match = db.query(User).filter(
        User.gender != me.gender,
        User.city == me.city,
        User.id != me.id
    ).order_by(User.is_premium.desc()).first()

    if not match:
        await message.answer("Afsuski, hozircha mos foydalanuvchi topilmadi.")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❤️ Like", callback_data=f"like_{match.id}"),
                InlineKeyboardButton(text="💔 Dislike", callback_data=f"dislike_{match.id}")
            ]
        ])
        await message.answer(
            f"👤 {match.name}, {match.age} yosh\n"
            f"📍 {match.city}\n"
            f"🎯 Qiziqishlari: {match.interests}",
            reply_markup=kb
        )
    db.close()

@router.callback_query(F.data.startswith("like_") | F.data.startswith("dislike_"))
async def handle_reaction(callback: types.CallbackQuery):
    db = SessionLocal()
    me = db.query(User).filter(User.telegram_id == callback.from_user.id).first()

    if not is_vip(me):
        await callback.message.answer("⛔ Bu funksiya faqat VIP foydalanuvchilar uchun.")
        await callback.answer()
        db.close()
        return

    target_id = int(callback.data.split("_")[1])
    is_like = callback.data.startswith("like")

    like = Like(from_user_id=me.id, to_user_id=target_id, is_like=is_like)
    db.add(like)
    db.commit()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Tanlovingiz saqlandi.")
    await callback.answer()
    db.close()

@router.message(lambda msg: msg.text.lower() == "kim menga like bosdi")
async def who_liked_me(message: types.Message):
    db = SessionLocal()
    me = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not is_vip(me):
        await message.answer("⛔ Bu funksiya faqat VIP foydalanuvchilar uchun.")
        db.close()
        return

    likes = db.query(Like).filter(
        Like.to_user_id == me.id,
        Like.is_like == True
    ).order_by(Like.timestamp.desc()).all()

    if not likes:
        await message.answer("🤷‍♂️ Hozircha sizga hech kim like bosmagan.")
    else:
        await message.answer("❤️ Sizga like bosganlar:")
        for like in likes[:10]:
            user = db.query(User).filter(User.id == like.from_user_id).first()
            if user:
                await message.answer(
                    f"👤 {user.name}, {user.age} yosh\n"
                    f"📍 {user.city}\n"
                    f"🕒 {like.timestamp.strftime('%Y-%m-%d %H:%M')}"
                )
    db.close()

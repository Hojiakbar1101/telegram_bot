from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import SessionLocal
from database.models import User
from datetime import datetime

router = Router()

@router.message(lambda msg: msg.text.lower() == "sozlamalar")
async def show_settings(message: types.Message):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"❤️ Like bildirishnomasi: {'✅' if user.notify_likes else '❌'}",
            callback_data="toggle_likes"
        )],
        [InlineKeyboardButton(
            text=f"💌 Moslik xabari: {'✅' if user.notify_matches else '❌'}",
            callback_data="toggle_matches"
        )],
        [InlineKeyboardButton(
            text=f"🕵️ Yashirin rejim: {'✅' if user.is_hidden else '❌'}",
            callback_data="toggle_hidden"
        )]
    ])
    await message.answer("🔧 Sozlamalar:", reply_markup=kb)
    db.close()

@router.callback_query(lambda c: c.data in ["toggle_likes", "toggle_matches", "toggle_hidden"])
async def toggle_settings(callback: types.CallbackQuery):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()

    if callback.data == "toggle_likes":
        user.notify_likes = not user.notify_likes
    elif callback.data == "toggle_matches":
        user.notify_matches = not user.notify_matches
    elif callback.data == "toggle_hidden":
        if not user.vip_until or user.vip_until < datetime.now():
            await callback.message.answer("⛔ Yashirin rejim faqat VIP foydalanuvchilar uchun.")
            await callback.answer()
            db.close()
            return
        user.is_hidden = not user.is_hidden

    db.commit()
    db.close()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Sozlama yangilandi. /sozlamalar buyrug‘i orqali qayta ko‘rishingiz mumkin.")
    await callback.answer()


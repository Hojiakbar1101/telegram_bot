from aiogram import Router, types, F
from database.db import SessionLocal
from database.models import User
from database.likes import Like

router = Router()

@router.callback_query(F.data.startswith("like_"))
async def handle_mutual_like(callback: types.CallbackQuery):
    db = SessionLocal()

    # 🧍‍♂️ Like bosgan foydalanuvchini olish
    me = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    if not me:
        await callback.message.answer("❗ Siz ro‘yxatdan o‘tmagansiz.")
        await callback.answer()
        db.close()
        return

    # 🎯 Target foydalanuvchini olish
    target_id = int(callback.data.split("_")[1])
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        await callback.message.answer("❗ Foydalanuvchi topilmadi.")
        await callback.answer()
        db.close()
        return

    # ❤️ Like yozish
    like = Like(from_user_id=me.id, to_user_id=target_id, is_like=True)
    db.add(like)
    db.commit()

    # 🔁 O‘zaro like borligini tekshirish
    mutual = db.query(Like).filter(
        Like.from_user_id == target_id,
        Like.to_user_id == me.id,
        Like.is_like == True
    ).first()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Like bosdingiz!")
    await callback.answer()

    if mutual:
        # 💌 O‘zaro like bo‘ldi — foydalanuvchiga habar
        target_username = f"@{target.telegram_username}" if target.telegram_username else "username mavjud emas"
        await callback.message.answer(
            f"🎉 Siz va {target.name} bir-biringizga yoqdingiz!\n"
            f"Telegram orqali bog‘laning: {target_username}"
        )

        # 💌 Target foydalanuvchiga habar yuborish
        me_username = f"@{me.telegram_username}" if me.telegram_username else "username mavjud emas"
        try:
            await callback.bot.send_message(
                chat_id=target.telegram_id,
                text=(
                    f"🎉 Siz va {me.name} bir-biringizga like bosdingiz!\n"
                    f"Telegram orqali bog‘laning: {me_username}"
                )
            )
        except:
            pass  # Agar foydalanuvchi botni bloklagan bo‘lsa

    db.close()

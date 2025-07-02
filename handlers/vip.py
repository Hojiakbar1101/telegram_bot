from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(lambda msg: msg.text.lower() == "vip")
async def vip_menu(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 1 kun - 5 000 so‘m", callback_data="vip_1")],
        [InlineKeyboardButton(text="💎 7 kun - 20 000 so‘m", callback_data="vip_7")],
        [InlineKeyboardButton(text="💎 30 kun - 50 000 so‘m", callback_data="vip_30")]
    ])
    await message.answer(
        "✨ *Sirli VIP tariflar* ✨\n\n"
        "VIP foydalanuvchilar quyidagilarga ega bo‘ladi:\n"
        "🔹 Profili ko‘proq ko‘rinadi\n"
        "🔹 Moslik algoritmida ustuvorlik\n"
        "🔹 Reklamasiz tajriba\n\n"
        "*Tarifni tanlang:*",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@router.callback_query(lambda c: c.data.startswith("vip_"))
async def process_vip(callback: types.CallbackQuery):
    days = int(callback.data.split("_")[1])
    amount = {1: 5000, 7: 20000, 30: 50000}[days]

    # Bu yerda Click yoki Payme havolasini generatsiya qilamiz
    payment_link = f"https://your-payment-gateway.uz/pay?amount={amount}&user_id={callback.from_user.id}&days={days}"

    await callback.message.answer(
        f"💳 *To‘lov tafsilotlari:*\n"
        f"📅 VIP muddati: {days} kun\n"
        f"💰 Narxi: {amount} so‘m\n\n"
        f"👇 Quyidagi havola orqali to‘lovni amalga oshiring:\n"
        f"[To‘lovni amalga oshirish]({payment_link})\n\n"
        f"✅ To‘lovdan so‘ng VIP avtomatik faollashadi.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

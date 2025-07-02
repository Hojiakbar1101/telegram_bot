from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.profile import ProfileStates  # ✅ to‘g‘ri
# ✅ FSM klassini import qilamiz

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Salom! Sirli Tanishuv botiga xush kelibsiz!\n"
        "Keling, siz haqingizda qisqacha ma’lumot to‘ldiramiz.\n"
        "Ismingizni yozing:"
    )
    await state.set_state(ProfileStates.name)  # ✅ FSM holatni boshlaymiz

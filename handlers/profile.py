from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import SessionLocal
from database.models import User
from utils.keyboards import gender_kb

router = Router()

class ProfileStates(StatesGroup):
    name = State()
    age = State()
    gender = State()
    interests = State()
    city = State()

async def collect_name(message: types.Message, state: FSMContext):
    await state.set_state(ProfileStates.name)
    await message.answer("Ismingizni kiriting:")

@router.message(ProfileStates.name)
async def collect_age(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProfileStates.age)
    await message.answer("Yoshingiz nechida?")

@router.message(ProfileStates.age)
async def collect_gender(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await state.set_state(ProfileStates.gender)
    await message.answer("Jinsingizni tanlang:", reply_markup=gender_kb)

@router.message(ProfileStates.gender)
async def collect_interests(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(ProfileStates.interests)
    await message.answer("Qiziqishlaringizni yozing (masalan: kitob, sport, IT):")

@router.message(ProfileStates.interests)
async def collect_city(message: types.Message, state: FSMContext):
    await state.update_data(interests=message.text)
    await state.set_state(ProfileStates.city)
    await message.answer("Qayerda yashaysiz?")

@router.message(ProfileStates.city)
async def save_profile(message: types.Message, state: FSMContext):
    data = await state.update_data(city=message.text)
    db = SessionLocal()
    user = User(
        telegram_id=message.from_user.id,
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        interests=data["interests"],
        city=data["city"],
        telegram_username=message.from_user.username 
    )
    db.add(user)
    db.commit()
    db.close()
    await state.clear()
    await message.answer("✅ Profilingiz saqlandi! Endi mos odamlarni qidiramiz.")

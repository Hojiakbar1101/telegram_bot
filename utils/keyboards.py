from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]
    ],
    resize_keyboard=True
)

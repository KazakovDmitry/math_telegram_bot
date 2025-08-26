from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_levels_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Легкий")],
            [KeyboardButton(text="Средний")],
            [KeyboardButton(text="Сложный")]
        ],
        resize_keyboard=True
    )
    return keyboard

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.handlers.math_training import MathTraining
from bot.keyboards.levels import get_levels_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Завершаем любое предыдущее состояние
    await message.answer(
        "Привет! Я бот для изучения математики.\n"
        "Давай решать примеры с разбиением чисел!\n"
        "Разбей числа правильно, чтобы легче было считать!\n\n"
        "Выбери уровень сложности:",
        reply_markup=get_levels_keyboard()
    )
    await state.set_state(MathTraining.waiting_for_level)

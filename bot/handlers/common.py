from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command("help"))
@router.message(lambda message: message.text and message.text.lower() == "помощь")
async def cmd_help(message: types.Message):
    await message.answer(
        "Я помогаю изучать математику через разбиение чисел.\n\n"
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n\n"
        "Выбери уровень сложности и начни решать примеры!",
        reply_markup=get_main_menu()
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено.",
        reply_markup=get_main_menu()
    )

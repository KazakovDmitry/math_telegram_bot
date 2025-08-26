from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.levels import get_levels_keyboard

# Глобальный словарь для хранения состояния пользователей (импортируем из math_training)
from bot.handlers.math_training import user_sessions

router = Router()


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Я помогаю изучать математику через разбиение чисел.\n\n"
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/cancel - отменить текущее действие\n\n"
        "Выбери уровень сложности и начни решать примеры!",
        reply_markup=get_main_menu()
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Отменяет текущее действие и сбрасывает состояние
    """
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нечего отменять. Вы не в процессе выполнения какой-либо операции.")
        return

    await state.clear()

    # Также очищаем сессию пользователя если она есть
    if message.from_user.id in user_sessions:
        del user_sessions[message.from_user.id]

    await message.answer(
        "Операция отменена. Вы можете начать заново с помощью /start",
        reply_markup=get_main_menu()
    )


@router.message()
async def handle_unexpected_messages(message: types.Message, state: FSMContext):
    """
    Обрабатывает все сообщения, которые не были обработаны другими обработчиками
    """
    current_state = await state.get_state()
    user_id = message.from_user.id

    # Логируем необработанное сообщение для отладки
    logging.info(f"Unhandled message from {user_id}: {message.text}")

    # Если состояние не установлено и пользователь не в сессии
    if current_state is None and user_id not in user_sessions:
        await message.answer(
            "🤖 Привет! Я бот для изучения математики.\n\n"
            "Я помогу тебе научиться решать примеры с разбиением чисел.\n\n"
            "Чтобы начать, напиши команду /start",
            reply_markup=types.ReplyKeyboardRemove()
        )
    # Если есть состояние, но сообщение не распознано
    elif current_state:
        state_name = current_state.split(":")[1] if ":" in current_state else current_state

        if "waiting_for_decomposition" in state_name:
            await message.answer(
                "Пожалуйста, введите разбиение числа в формате 'X Y' (два числа через пробел)\n"
                "Или напишите 'подсказка' для помощи"
            )
        elif "waiting_for_answer" in state_name:
            await message.answer(
                "Пожалуйста, введите числовой ответ на пример"
            )
        elif "waiting_for_level" in state_name:
            await message.answer(
                "Пожалуйста, выберите уровень сложности из предложенных вариантов:",
                reply_markup=get_levels_keyboard()
            )
        else:
            await message.answer(
                "Я не понял ваш запрос в текущем состоянии.\n"
                "Пожалуйста, используйте кнопки меню или введите корректные данные.\n"
                "Если хотите начать заново, напишите /start"
            )
    # Любой другой случай
    else:
        await message.answer(
            "Я не понял ваш запрос.\n\n"
            "Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/help - показать справку\n"
            "/cancel - отменить текущее действие\n\n"
            "Или используйте кнопки меню для навигации.",
            reply_markup=get_main_menu()
        )
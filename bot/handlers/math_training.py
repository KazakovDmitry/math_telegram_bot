from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from math_tutor import MathTutor
from bot.keyboards.levels import get_levels_keyboard
from bot.keyboards.main_menu import get_main_menu

router = Router()


# Состояния для FSM
class MathTraining(StatesGroup):
    waiting_for_level = State()
    waiting_for_decomposition = State()
    waiting_for_answer = State()


# Глобальный словарь для хранения состояния пользователей
user_sessions = {}


@router.message(lambda message: message.text in ["Легкий", "Средний", "Сложный"])
async def select_level(message: types.Message, state: FSMContext):
    level = message.text
    tutor = MathTutor(level)
    user_sessions[message.from_user.id] = {
        "tutor": tutor,
        "level": level,
        "attempts": 0  # Счетчик попыток
    }

    await state.set_state(MathTraining.waiting_for_decomposition)
    await message.answer(f"Максимальное количество ошибок: {tutor.max_attempts}")
    await generate_example(message, state)


async def generate_example(message: types.Message, state: FSMContext):
    user_data = user_sessions.get(message.from_user.id)
    if not user_data:
        await message.answer("Сначала выбери уровень сложности:", reply_markup=get_levels_keyboard())
        await state.set_state(MathTraining.waiting_for_level)
        return

    tutor = user_data["tutor"]
    a, b, op, needs_decomp = tutor.generate_example()
    result = tutor.calculate(a, b, op)

    parts = 0
    if needs_decomp:
        parts = tutor.decompose(a, b, op)
        if op == '+' and parts[0] == 0:
            needs_decomp = False

    # Сохраняем данные примера в состоянии пользователя
    user_data["current_example"] = {
        "a": a, "b": b, "op": op,
        "result": result, "needs_decomp": needs_decomp,
        "parts": parts
    }

    # Сбрасываем счетчик попыток для нового примера
    user_data["attempts"] = 0

    # Отправляем пример пользователю
    example_text = f"Пример: {a} {op} {b}"

    if needs_decomp:
        hint_text = f"Разбей {b} на {parts[0]} и {parts[1]}"

        if tutor.hint_mode == "always":
            example_text += f"\n{hint_text}"
        elif tutor.hint_mode == "on_request":
            example_text += "\nНапиши 'подсказка' для помощи"

        await message.answer(example_text, reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Введи разбиение (два числа через пробел): ")
        await state.set_state(MathTraining.waiting_for_decomposition)
    else:
        await message.answer(example_text, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(MathTraining.waiting_for_answer)


@router.message(MathTraining.waiting_for_decomposition)
async def handle_decomposition(message: types.Message, state: FSMContext, attempts=0):
    user_data = user_sessions.get(message.from_user.id)
    if not user_data or "current_example" not in user_data:
        await message.answer("Что-то пошло не так. Давай начнем сначала.", reply_markup=get_main_menu())
        await state.clear()
        return

    example = user_data["current_example"]
    tutor = user_data["tutor"]

    # Получаем текущее количество попыток
    attempts = user_data.get("attempts", 0)

    hint_text = f"Разбей {example['b']} на {example['parts'][0]} и {example['parts'][1]}"

    # Обработка запроса подсказки
    if message.text.lower() == 'подсказка' and tutor.hint_mode == 'on_request':
        await message.answer(hint_text)
        await message.answer("Введи разбиение (два числа через пробел):")
        return

    # Проверяем, не ввел ли пользователь сразу ответ
    try:
        user_answer = int(message.text)
        if user_answer == example["result"]:
            await message.answer(f"🌟 Отлично! {example['a']} {example['op']} {example['b']} = {example['result']}")
            await message.answer("Хочешь еще пример?", reply_markup=get_main_menu())
            await state.clear()
            return
        else:
            await message.answer("❌ Неверно! Попробуй разбить число правильно.")
            await message.answer("Введи разбиение (два числа через пробел):")
            return
    except ValueError:
        pass  # Не число, продолжаем проверку разбиения

    # Проверка разбиения
    if tutor.validate_decomposition(message.text, example['parts']):
        await message.answer("✅ Верно! Теперь посчитаем по шагам.")

        # Показываем пошаговое решение
        if example['op'] == '-':
            await message.answer(
                f"{example['a']} - {example['b']} = {example['a']} - ({example['parts'][0]} + {example['parts'][1]})")
            await message.answer(
                f"Шаг 1: {example['a']} - {example['parts'][0]} = {example['a'] - example['parts'][0]}")
            await message.answer(f"Шаг 2: {example['a'] - example['parts'][0]} - {example['parts'][1]} = ?")
        else:
            await message.answer(
                f"{example['a']} + {example['b']} = {example['a']} + ({example['parts'][0]} + {example['parts'][1]})")
            await message.answer(
                f"Шаг 1: {example['a']} + {example['parts'][0]} = {example['a'] + example['parts'][0]}")
            await message.answer(f"Шаг 2: {example['a'] + example['parts'][0]} + {example['parts'][1]} = ?")

        await message.answer("Сколько получилось?")
        await state.set_state(MathTraining.waiting_for_answer)
    else:
        # Увеличиваем счетчик попыток
        attempts += 1
        user_data["attempts"] = attempts

        await message.answer(f"❌ Неверно! Количество ошибок {attempts} из {tutor.max_attempts}")

        if attempts < tutor.max_attempts:
            if tutor.hint_mode == "on_error" or tutor.hint_mode == "always":
                await message.answer(hint_text)
            await message.answer("Введи разбиение (два числа через пробел):")
        else:
            await message.answer(f"Правильное разбиение: {example['parts'][0]} и {example['parts'][1]}")
            await message.answer("Хочешь еще пример?", reply_markup=get_main_menu())
            await state.clear()


@router.message(MathTraining.waiting_for_answer)
async def handle_answer(message: types.Message, state: FSMContext):
    user_data = user_sessions.get(message.from_user.id)
    if not user_data or "current_example" not in user_data:
        await message.answer("Что-то пошло не так. Давай начнем сначала.", reply_markup=get_main_menu())
        await state.clear()
        return

    example = user_data["current_example"]

    try:
        user_answer = int(message.text)
        if user_answer == example["result"]:
            await message.answer(f"🌟 Отлично! {example['a']} {example['op']} {example['b']} = {example['result']}")
        else:
            await message.answer(f"❌ Неверно! Правильный ответ: {example['result']}")
    except ValueError:
        await message.answer("Пожалуйста, введи число.")
        await message.answer("Сколько получилось?")
        return

    # Предлагаем новый пример
    await message.answer("Хочешь еще пример?", reply_markup=get_main_menu())
    await state.clear()


@router.message(lambda message: message.text and message.text.lower() == "новый пример")
async def new_example(message: types.Message, state: FSMContext):
    user_data = user_sessions.get(message.from_user.id)
    if not user_data:
        await message.answer("Сначала выбери уровень сложности:", reply_markup=get_levels_keyboard())
        await state.set_state(MathTraining.waiting_for_level)
        return

    await state.set_state(MathTraining.waiting_for_decomposition)
    await generate_example(message, state)


@router.message(lambda message: message.text and message.text.lower() == "сменить уровень")
async def change_level(message: types.Message, state: FSMContext):
    await message.answer("Выбери уровень сложности:", reply_markup=get_levels_keyboard())
    await state.set_state(MathTraining.waiting_for_level)

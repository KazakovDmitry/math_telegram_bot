import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.handlers import router

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Создаем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Все сообщения уровня INFO и выше
console_handler.setFormatter(formatter)

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)  # Все сообщения уровня DEBUG и выше
file_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутер
    dp.include_router(router)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())

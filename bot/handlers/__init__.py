from aiogram import Router
from . import start, common,  math_training

# Создаем главный роутер
router = Router()

# Подключаем обработчики из модулей
router.include_router(start.router)
router.include_router(math_training.router)
router.include_router(common.router)

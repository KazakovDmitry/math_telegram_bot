import logging
import random
import re


class MathTutor:
    """
    Класс для генерации и решения математических примеров для детей
    с использованием методики разбиения чисел.
    """
    MIN_OPERAND = 3
    MAX_ADD_OPERAND = 9
    MAX_SUB_OPERAND = 19
    DECOMPOSE_THRESHOLD = 10

    # Уровни сложности
    LEVELS = {
        "Легкий": {"hint_mode": "always", "max_attempts": 4},
        "Средний": {"hint_mode": "on_error", "max_attempts": 3},
        "Сложный": {"hint_mode": "on_request", "max_attempts": 2}
    }

    def __init__(self, level="Средний"):
        self.level = level
        self.hint_mode = self.LEVELS[level]["hint_mode"]
        self.max_attempts = self.LEVELS[level]["max_attempts"]

    def generate_example(self):
        """
        Генерирует математический пример (сложение или вычитание)
        Возвращает:
            a (int), b (int), operation (str), needs_decomposition (bool)
        """
        operation = random.choice(['+', '-'])

        if operation == '+':
            a = random.randint(self.MIN_OPERAND, self.MAX_ADD_OPERAND)
            b = random.randint(self.MIN_OPERAND, self.MAX_ADD_OPERAND)
            needs_decomposition = (a + b) > self.DECOMPOSE_THRESHOLD
        elif operation == '-':
            a = random.randint(self.DECOMPOSE_THRESHOLD + 1, self.MAX_SUB_OPERAND)
            b = random.randint(self.MIN_OPERAND, self.MAX_ADD_OPERAND)
            needs_decomposition = (a - b) < self.DECOMPOSE_THRESHOLD

        return a, b, operation, needs_decomposition

    def decompose(self, a: int, b: int, operation: str) -> tuple:
        """
        Разбивает число на две части по методике дополнения до 10
        Возвращает: (part1, part2)
        """
        if operation == "-":
            to_ten = a - self.DECOMPOSE_THRESHOLD
            return to_ten, b - to_ten

        if operation == "+":
            to_ten = self.DECOMPOSE_THRESHOLD - a
            if 0 < to_ten <= b:
                return to_ten, b - to_ten
            return 0, b  # Разбиение не требуется

    def calculate(self, a: int, b: int, operation: str) -> int:
        """
        Вычисляет результат примера, возможно с использованием разбиения
        """
        if operation == '-':
            return a - b
        if operation == '+':
            return a + b

    # def validate_decomposition(self, user_input: str, expected_parts: tuple) -> bool:
    #     """
    #     Проверяет правильность разбиения числа пользователем
    #     """
    #     try:
    #         user_parts = tuple(map(int, user_input.split()))
    #         return user_parts == expected_parts
    #     except (ValueError, TypeError):
    #         return False

    def validate_decomposition(self, user_input: str, expected_parts: tuple) -> bool:
        """
        Проверяет правильность разбиения числа пользователем
        с улучшенной обработкой ввода и логированием
        """
        try:
            # Логируем ввод и ожидаемые значения
            logging.debug(f"User input: '{user_input}', expected: {expected_parts}")

            # Удаляем все нецифровые символы, кроме пробелов
            cleaned_input = re.sub(r'[^\d\s]', '', user_input.strip())
            logging.debug(f"Cleaned input: '{cleaned_input}'")

            # Разбиваем на части и фильтруем пустые строки
            parts = [p for p in cleaned_input.split() if p]
            logging.debug(f"Parsed parts: {parts}")

            if len(parts) != 2:
                logging.debug(f"Invalid number of parts: {len(parts)}")
                return False

            user_parts = tuple(map(int, parts))
            logging.debug(f"User parts as integers: {user_parts}")

            # Проверяем оба варианта порядка чисел
            is_valid = (user_parts == expected_parts or
                        user_parts == expected_parts[::-1])

            logging.debug(f"Validation result: {is_valid}")
            return is_valid

        except (ValueError, TypeError) as e:
            logging.debug(f"Validation error: {e}")
            return False

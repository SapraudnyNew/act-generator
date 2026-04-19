"""
validator.py

Валидация JSON-данных из экстрактора.

Что проверяет:
  1. Наличие обязательных полей
  2. hours * rate == total_amount (с допустимым отклонением)
  3. Интерактивный запрос недостающих данных через input()
"""

from __future__ import annotations

from typing import Any

# Обязательные поля на верхнем уровне
_REQUIRED_TOP = [
    "invoice_number",
    "invoice_date",
    "act_date",
    "service_name",
    "total_amount",
    "currency",
]

# Обязательные поля внутри contractor / client
_REQUIRED_PARTY = ["name", "inn", "address"]

# Поля, которые нужны для подписанта (если null — спросим)
_SIGNATORY_FIELDS = ["signatory", "position"]

# Допустимое отклонение при проверке hours * rate
_MATH_TOLERANCE = 0.02  # 2%


def _ask(prompt: str) -> str:
    """Интерактивный запрос пользователю. Не принимает пустую строку."""
    while True:
        value = input(f"\n❓ {prompt}: ").strip()
        if value:
            return value
        print("  Не может быть пустым. Попробуй ещё.")


def _fill_missing(data: dict, keys: list[str], prefix: str = "") -> None:
    """Для каждого null-поля из keys спрашивает пользователя."""
    for key in keys:
        if not data.get(key):
            label = f"{prefix}{key}" if prefix else key
            data[key] = _ask(f"Введи {label}")


def validate(data: dict[str, Any]) -> dict[str, Any]:
    """
    Валидирует и при необходимости дополняет данные через input().
    Возвращает обогащённый dict.
    """
    # 1. Обязательные поля верхнего уровня
    _fill_missing(data, _REQUIRED_TOP)

    # 2. Обязательные поля сторон
    for party in ("contractor", "client"):
        if party not in data or not isinstance(data[party], dict):
            data[party] = {}
        _fill_missing(data[party], _REQUIRED_PARTY, prefix=f"{party}.")     
        _fill_missing(data[party], _SIGNATORY_FIELDS, prefix=f"{party}.")

    # 3. Математическая проверка hours * rate == total_amount
    hours = data.get("hours")
    rate = data.get("rate")
    total = data.get("total_amount")

    if hours is not None and rate is not None and total is not None:
        calculated = float(hours) * float(rate)
        expected = float(total)
        if expected != 0:
            deviation = abs(calculated - expected) / expected
            if deviation > _MATH_TOLERANCE:
                print(
                    f"\n⚠️  Математика не сходится:"
                    f" {hours} ч × {rate} = {calculated:.2f},"
                    f" а в счёте указано {expected:.2f}"
                    f" (отклонение {deviation*100:.1f}%)"
                )
                choice = input("Продолжаем? [да/нет]: ").strip().lower()
                if choice not in ("d", "д", "yes", "y", "1"):
                    raise ValueError("Остановлено пользователем: несоответствие суммы")

    return data

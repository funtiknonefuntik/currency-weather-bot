from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CURRENCIES = ["USD", "EUR", "CNY", "GBP"]


def currencies_kb() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=code, callback_data=f"rate:{code}")
        for code in CURRENCIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons[:2], buttons[2:]])
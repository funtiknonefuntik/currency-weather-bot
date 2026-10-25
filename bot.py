import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import BotCommand, CallbackQuery, Message
from api import get_rates, get_weather, get_forecast
from config import BOT_TOKEN, CHAT_ID
from keyboards import currencies_kb
from converter import convert, parse_query
from datetime import date
from api import get_rates, get_rates, get_weather
from scheduler import daily_digest




logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


@dp.message(Command("id"))
async def id_cmd(message: Message):
    await message.answer(f"Ваш chat id: {message.chat.id}")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Что я умею:\n"
        "/rate: курс валют ЦБ РФ\n"
        "/convert 100 USD EUR: конвертер\n"
        "/forecast Москва: Прогноз на 5 дней\n"
        "/weather Москва: погода в городе"
    )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я показываю курсы валют ЦБ РФ.\nКоманда: /rate")


@dp.message(Command("rate"))
async def rate_cmd(message: Message):
    await message.answer("Выберите валюту:", reply_markup=currencies_kb())


@dp.callback_query(F.data.startswith("rate:"))
async def show_rate(callback: CallbackQuery):
    code = callback.data.split(":")[1]
    try:
        rates = await get_rates()
    except Exception:
        logging.exception("Не удалось получить курсы")
        await callback.answer("Сервис недоступен, попробуйте позже", show_alert=True)
        return
    await callback.message.answer(f"1 {code} = {rates[code]:.2f} ₽")
    await callback.answer()

@dp.message(Command("convert"))
async def convert_cmd(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Формат: /convert 100 USD EUR")
        return
    try:
        amount, from_code, to_code = parse_query(command.args)
    except ValueError:
        await message.answer("Не понял. Пример: /convert 100 USD EUR")
        return
    try:
        rates = await get_rates()
    except Exception:
        logging.exception("Не удалось получить курсы")
        await message.answer("Сервис недоступен, попробуйте позже")
        return
    if from_code not in rates or to_code not in rates:
        await message.answer("Такой валюты нет. Примеры: USD, EUR, CNY, RUB")
        return
    result = convert(amount, from_code, to_code, rates)
    await message.answer(f"{amount:g} {from_code} = {result:.2f} {to_code}")

@dp.message(Command("weather"))
async def weather_cmd(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Формат: /weather Москва")
        return
    try:
        w = await get_weather(command.args.strip())
    except Exception:
        logging.exception("Не удалось получить погоду")
        await message.answer("Сервис недоступен, попробуйте позже")
        return
    if w is None:
        await message.answer("Город не найден. Проверьте название.")
        return
    await message.answer(
        f"{w['city']}, {w['country']}\n"
        f"{w['description']}\n"
        f"🌡 {w['temp']:.0f}°C (ощущается как {w['feels']:.0f}°C)\n"
        f"💨 ветер {w['wind']:.0f} м/с\n"
        f"💧 влажность {w['humidity']:.0f}%"
    )

@dp.message(Command("forecast"))
async def forecast_cmd(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Формат: /forecast Москва")
        return
    try:
        f = await get_forecast(command.args.strip())
    except Exception:
        logging.exception("Не удалось получить прогноз")
        await message.answer("Сервис недоступен, попробуйте позже")
        return
    if f is None:
        await message.answer("Город не найден. Проверьте название")
        return
    lines = [f"Прогноз: {f['city']}, {f['country']}"]
    for day in f["days"]:
        d = date.fromisoformat(day["date"])
        rain = "--" if day["rain"] is None else f"{day['rain']:.0f}%"
        lines.append(
            f"{WEEKDAYS[d.weekday()]} {d:%d.%m}: {day['description']}, "
            f"{day['min']:.0f}...{day['max']:.0f}°C, осадки {rain}"
        )
    await message.answer("\n".join(lines))


async def main():
    bot = Bot(BOT_TOKEN)
    await bot.set_my_commands([
        BotCommand(command="rate", description="Курс валют"),
        BotCommand(command="convert", description="Конвертер валют"),
        BotCommand(command="weather", description="Погода в городе"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="forecast", description="Прогноз на 5 дней"),
    ])
    if CHAT_ID:
        task = asyncio.create_task(daily_digest(bot))
    await dp.start_polling(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

















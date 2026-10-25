import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from api import get_forecast, get_rates, get_weather
from config import CHAT_ID, CITY, DIGEST_TIME, TZ

async def build_digest() -> str:
    w = await get_weather(CITY)
    f = await get_forecast(CITY, days=1)
    if w is None or f is None:
        return f"Не удалось найти город {CITY}"
    rates = await get_rates()
    today = f["days"][0]
    rain = "--" if today["rain"] is None else f"{today['rain']:.0f}%"
    return (
        f"Доброе утро! {w['city']}\n"
        f"Сейчас: {w['description']}, {w['temp']:.0f}°C\n"
        f"Днём: {today['min']:.0f}…{today['max']:.0f}°C, осадки {rain}\n\n"
        f"USD: {rates['USD']:.2f} ₽\n"
        f"EUR: {rates['EUR']:.2f} ₽"
    )
def seconds_until(time_str: str, tz_name: str) -> float:
    now = datetime.now(ZoneInfo(tz_name))
    hour, minute = map(int, time_str.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()

async def daily_digest(bot: Bot):
    while True:
        await asyncio.sleep(seconds_until(DIGEST_TIME, TZ))
        try:
            await bot.send_message(CHAT_ID, await build_digest())
        except Exception:
            logging.exception("Не удалось отправить утреннюю сводку")
        await asyncio.sleep(1)
















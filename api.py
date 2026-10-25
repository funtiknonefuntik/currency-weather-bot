import asyncio
import aiohttp
import time

from aiogram.dispatcher.middlewares import data

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_FIELDS = [
    "temperature_2m",
    "apparent_temperature",
    "wind_speed_10m",
    "weather_code",
    "relative_humidity_2m"
]

DAILY_FIELDS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_probability_max"
]

CACHE_TTL = 600  # секунд
_cache = {"rates": None, "time": 0.0}

async def get_rates() -> dict:
    now = time.monotonic()
    if _cache["rates"] and now - _cache["time"] > CACHE_TTL:
        return _cache["rates"]

    async with aiohttp.ClientSession() as session:
        async with session.get(CBR_URL) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)

    rates = {"RUB": 1.0}
    for code, info in data["Valute"].items():
        rates[code] = info["Value"] / info["Nominal"]
    return rates


def describe_weather(code: int) -> str:
    if code == 0:
        return "ясно ☀️"
    if code in (1, 2):
        return "малооблачно 🌤"
    if code == 3:
        return "пасмурно ☁️"
    if code in (45, 48):
        return "туман 🌫"
    if 51 <= code <= 57:
        return "морось 🌦"
    if 61 <= code <= 67 or 80 <= code <= 82:
        return "дождь 🌧"
    if 71 <= code <= 77 or code in (85, 86):
        return "снег ❄️"
    if code >= 95:
        return "гроза ⛈"
    return "погода без описания"

async def _find_city(session: aiohttp.ClientSession, city: str) -> dict | None:
    params = {"name": city, "count": 1, "language": "ru"}
    async with session.get(GEO_URL, params=params) as resp:
        resp.raise_for_status()
        geo = await resp.json()
    places = geo.get("results")
    return places[0] if places else None


async def get_weather(city: str) -> dict | None:
    async with aiohttp.ClientSession() as session:
        place = await _find_city(session, city)
        if place is None:
            return None
        params = {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": ",".join(CURRENT_FIELDS),
            "wind_speed_unit": "ms",
            "timezone": "auto",
        }
        async with session.get(FORECAST_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    current = data["current"]
    return {
        "city": place["name"],
        "country": place.get("country", ""),
        "temp": current["temperature_2m"],
        "feels": current["apparent_temperature"],
        "wind": current["wind_speed_10m"],
        "humidity": current["relative_humidity_2m"],
        "description": describe_weather(current["weather_code"]),
    }


async def get_forecast(city: str, days: int = 5) -> dict | None:
    async with aiohttp.ClientSession() as session:
        place = await _find_city(session, city)
        if place is None:
            return None
        params = {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "daily": ",".join(DAILY_FIELDS),
            "forecast_days": days,
            "timezone": "auto",
        }
        async with session.get(FORECAST_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    daily = data["daily"]
    forecast = []
    for i, day in enumerate(daily["time"]):
        forecast.append({
            "date": day,
            "min": daily["temperature_2m_min"][i],
            "max": daily["temperature_2m_max"][i],
            "rain": daily["precipitation_probability_max"][i],
            "description": describe_weather(daily["weather_code"][i]),
        })
    return {
        "city": place["name"],
        "country": place.get("country", ""),
        "days": forecast,
    }









if __name__ == "__main__":
    rates = asyncio.run(get_rates())
    print("USD:", rates["USD"])
    print("EUR:", rates["EUR"])
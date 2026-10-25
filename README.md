# Бот: курсы валют, погода и утренняя сводка

Telegram-бот на Python (aiogram 3, aiohttp).

## Возможности
- /rate: курс валют ЦБ РФ
- /convert 100 USD EUR: конвертер
- /weather Москва: погода сейчас
- /forecast Москва: прогноз на 5 дней
- Каждое утро в заданное время присылает сводку: погоду и курсы

## Запуск
1. Создайте бота у @BotFather и получите токен.
2. Скопируйте .env.example в .env и заполните значения.
   Свой CHAT_ID можно узнать командой /id.
3. python -m venv venv
4. venv\Scripts\activate
5. pip install -r requirements.txt
6. python bot.py

## Источники данных
- Курсы: cbr-xml-daily.ru
- Погода: open-meteo.com
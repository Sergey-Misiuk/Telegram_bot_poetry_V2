#!/bin/sh


echo "Starting server API."
poetry run uvicorn 0.0.0.0:8000 backend.api.main:app

echo "Starting server Telegram_bot."
poetry run python bot.main.py

import streamlit as st
import httpx
import logging
import asyncio
import threading
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройки Telegram Bot
BOT_TOKEN = "7897738368:AAHCYVdHyJCudXQNqzKEuYBM_hXB8vs0GBg"
TELEGRAM_CHAT_ID = "-4709248843"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)

def run_asyncio_coroutine(coroutine):
    """Запускает асинхронную функцию в новом цикле событий."""
    try:
        return asyncio.run(coroutine)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)

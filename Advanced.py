import streamlit as st
import httpx
import logging
import asyncio
import threading
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain.chains import LLMChain
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Настройки Telegram Bot
BOT_TOKEN = "7897738368:AAHCYVdHyJCudXQNqzKEuYBM_hXB8vs0GBg"
TELEGRAM_CHAT_ID = "-4709248843"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
llm = Ollama(model="llama2")

# Настройка памяти с использованием LangChain
memory = ConversationBufferMemory()

summary_prompt = PromptTemplate(
    input_variables=["text"],
    template="Составь краткое резюме следующего текста: {text}. Выдели главные темы, аргументы и тезисы."
)

def run_asyncio_coroutine(coroutine):
    """Запускает асинхронную функцию в новом цикле событий."""
    try:
        return asyncio.run(coroutine)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)

async def get_ollama_response(prompt: str) -> str:
    """Отправляет запрос в Ollama API и возвращает ответ."""
    try:
        payload = {"model": "llama2", "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.post(OLLAMA_API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response received from Ollama.")
            else:
                return f"Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Exception occurred: {e}"

async def summarize_text(text: str) -> str:
    """Генерирует резюме текста."""
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
    summary = summary_chain.run(text=text).strip()
    return summary

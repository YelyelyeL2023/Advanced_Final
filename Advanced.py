import streamlit as st
import httpx
import logging
import asyncio
import threading
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain.chains import LLMChain
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Настройки Telegram Bot
BOT_TOKEN = "7897738368:AAHCYVdHyJCudXQNqzKEuYBM_hXB8vs0GBg"
TELEGRAM_CHAT_ID = "1318055116"
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
    template="Составь краткое резюме следующего текста: {text}. Выдели главные темы, аргументы и тезисы. Если пользователь запрашивает верни ему тот же текст с памяти хранение"
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

async def send_message_to_telegram(text: str):
    """Отправляет сообщение в Telegram-бот."""
    max_length = 4096
    for i in range(0, len(text), max_length):
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text[i:i+max_length])

async def start(update: Update, context: CallbackContext):
    """Обрабатывает команду /start."""
    await update.message.reply_text("Привет! Я бот с Ollama. Отправьте мне текст, и я сделаю его резюме.")

async def handle_message(update: Update, context: CallbackContext):
    """Обрабатывает входящее сообщение, отправляет его в Ollama и создает резюме."""
    user_input = update.message.text
    memory.save_context({"input": user_input}, {})
    context_text = memory.load_memory_variables({}).get("history", "")
    full_prompt = f"История: {context_text}\nНовый запрос: {user_input}"
    summary = await summarize_text(full_prompt)
    response = await get_ollama_response(summary)
    await update.message.reply_text(response)
    await send_message_to_telegram(f"Пользователь отправил текст: {user_input}\nКраткое резюме: {summary}")
    memory.save_context({"input": user_input}, {"output": response})

async def process_streamlit_query(query: str):
    """Обрабатывает запрос из Streamlit: создает резюме и получает ответ."""
    summary = await summarize_text(query)
    response = await get_ollama_response(summary)
    await send_message_to_telegram(f"Streamlit запрос: {query}\nКраткое резюме: {summary}")
    return response



async def run_telegram_bot():
    """Запускает Telegram-бота в фоновом режиме."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Telegram bot запущен!")
    await app.run_polling()

# Интерфейс Streamlit
st.title("LLM Telegram Chatbot")
user_input = st.text_area("Введите большой текст для анализа:")

if st.button("Составить резюме"):
    if user_input:
        response = run_asyncio_coroutine(process_streamlit_query(user_input))
        st.write("### Краткое резюме:")
        st.write(response)
    else:
        st.warning("Введите текст перед отправкой!")

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_telegram_bot()), daemon=True).start()

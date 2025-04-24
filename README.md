# LLM Telegram Chatbot

This project is a Telegram bot and Streamlit web app that generates concise summaries of large texts using an LLM (Ollama with Llama2). It supports both Telegram chat and a web interface, and sends summaries to a specified Telegram chat.

## Features

- Summarizes large texts using Llama2 via Ollama API.
- Remembers conversation history for context-aware summaries.
- Telegram bot interface for interactive chat.
- Streamlit web interface for easy text input and summary display.
- Sends all summaries to a specified Telegram chat.

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running Llama2 model
- Telegram Bot Token and Chat ID

## Installation

1. Clone the repository.
2. Install dependencies:
   ```
   pip install streamlit httpx python-telegram-bot langchain
   ```
3. Set your Telegram bot token and chat ID in `Advanced.py`:
   ```python
   BOT_TOKEN = "YOUR_TOKEN"
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
   ```

## Usage

1. Start Ollama with the Llama2 model.
2. Run the app:
   ```
   streamlit run Advanced.py
   ```
3. The Telegram bot will start automatically in the background.

## File Overview

- `Advanced.py`: Main application file containing both Streamlit and Telegram bot logic.

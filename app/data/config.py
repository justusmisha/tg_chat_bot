import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

REDIS_URL = os.getenv('REDIS_URL')

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

WAITING_MESSAGE = "⏳ GPT-4o генерирует ответ. Пожалуйста, подождите немного . . ."

CH_DB_NAME=os.getenv('CH_DB_NAME')
CH_HOST=os.getenv('CH_HOST')
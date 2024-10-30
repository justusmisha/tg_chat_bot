import re
from typing import List, Dict

from openai import OpenAI

from app.data.config import OPENAI_API_KEY
from app_logging import logger


def replace_bold_with_html(message_text):
    # Regex to replace text wrapped in double asterisks with <b>...</b>
    updated_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', message_text)
    return updated_text


def format_history_for_api(history: List[Dict[str, str]], max_messages: int = 10) -> List[Dict[str, str]]:
    formatted_history = history[-max_messages:]

    messages = []
    for entry in formatted_history:
        messages.append({
            'role': entry['role'],
            'content': entry['content']
        })

    return messages

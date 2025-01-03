from typing import Dict, List

from openai import OpenAI

from app.data.config import OPENAI_API_KEY
from app.utils.text_changes import format_history_for_api
from app_logging import logger


async def gpt_4o_mini(history: List[Dict[str, str]]):
    client = OpenAI(api_key=OPENAI_API_KEY)

    history.insert(0, {"role": "system", "content": "Ты полезный ассистент, который общается на русском."})

    logger.info(f'Passing formatted messages to GPT-4: {history}')

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history
    )

    return completion.choices[0].message.content


async def summarize_context(history: List[Dict[str, str]]) -> str:

    combined_text = ' '.join(entry['content'] for entry in history)

    client = OpenAI(api_key=OPENAI_API_KEY)

    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 'content': 'Please summarize the following conversation.'},
            {'role': 'user', 'content': combined_text}
        ]
    )
    return summary_response.choices[0].message.content
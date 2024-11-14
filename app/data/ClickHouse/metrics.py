from datetime import date

from app.data.ClickHouse.initialization import client
from app_logging import logger


async def log_unique_user(user_id):
    data = [user_id, date.today()]
    columns = ['user_id', 'date_start']
    try:
        query = f"SELECT * FROM bot_metrics WHERE user_id = {user_id} LIMIT 1"
        result = client.query(query)
        if not result.result_rows:
            client.insert('bot_metrics', data=[data], column_names=columns)

    except Exception as e:
        logger.error(f"Error occurred during insert: {e}")


async def log_metrics(user_id, **kwargs):

    data = [user_id]

    optional_metrics = {
        'count_requests': 0,
        'count_words_requests': 0,
        'count_words_response': 0,
        'history': kwargs.get('history', [])
    }

    for metric, default_value in optional_metrics.items():
        data.append(kwargs.get(metric, default_value) if metric != 'history' else optional_metrics['history'])

    query = f"SELECT * FROM bot_metrics WHERE user_id = {user_id} LIMIT 1"
    result = client.query(query)
    if result.result_rows:
        new_count_requests = result.result_rows[0][2] + kwargs.get('count_requests', 0)
        new_count_words_requests = result.result_rows[0][3] + kwargs.get('count_words_requests', 0)
        new_count_words_response = result.result_rows[0][4] + kwargs.get('count_words_response', 0)
        new_history = optional_metrics['history']

        update_query = f"""
            ALTER TABLE bot_metrics UPDATE
                count_requests = {new_count_requests},
                count_words_requests = {new_count_words_requests},
                count_words_response = {new_count_words_response},
                history = '{new_history}'
            WHERE user_id = {user_id};
        """

        client.query(update_query)


async def get_user_history(user_id):
    try:
        query = f"""
        SELECT history
        FROM bot_metrics
        WHERE user_id = {user_id}
        LIMIT 1
        """
        result = client.query(query)

        if result.result_rows:
            user_history = result.result_rows[0][0] if result.result_rows[0][0] else ''
            return user_history
        else:
            return []
    except Exception as e:
        logger.error(f"Error in getting history: {e}")
        return []


async def clear_user_history(user_id):
    try:
        query = f"""
        SELECT history
        FROM bot_metrics
        WHERE user_id = {user_id}
        LIMIT 1
        """
        result = client.query(query)

        if result.result_rows:
            update_query = f"""
                                    ALTER TABLE bot_metrics UPDATE
                                        history = ''
                                    WHERE user_id = {user_id};
                                """

            client.query(update_query)
            return True
        else:
            return False
        
    except Exception as e:
        logger.error(f"Error in deleting history: {e}")
        return []

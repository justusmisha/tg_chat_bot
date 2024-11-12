import time
from datetime import datetime

from app.data.ClickHouse.initialization import log_metric, client
from app.loader import redis_client


def log_unique_user(user_id):
    query = f"SELECT * FROM bot_metrics WHERE user_id = {user_id} AND metric_type = 'unique_user'"
    users = client.query(query)
    if not users.result_rows:
        log_metric(user_id=user_id, metric_type="unique_user", count=1)


async def log_response_time(user_id, start_time):
    response_time = time.time() - start_time
    response_time = response_time if response_time is not None else 0.0
    log_metric(user_id, "response_time", response_time=response_time)


def log_error(user_id, error_message):
    log_metric(user_id, "error", count=1)


async def log_message_count_in_clickhouse(user_id, message_length):
    query = f"SELECT * FROM bot_metrics WHERE user_id = {user_id} AND metric_type = 'message_count_and_length' LIMIT 1"
    result = client.query(query)

    if result.result_rows:
        new_count = result.result_rows[0][2] + 1
        new_avr_length = result.result_rows[0][5] + message_length
        print(result.result_rows)
        print((result.result_rows[0][5] + message_length), (result.result_rows[0][2] + 1))

        client.query(f"""
            ALTER TABLE bot_metrics UPDATE 
                count = {new_count}, 
                message_length = {new_avr_length} 
            WHERE user_id = {user_id} AND metric_type = 'message_count_and_length'
        """)
    else:
        client.insert(
            'bot_metrics',
            [[user_id, "message_count_and_length", 1, message_length, datetime.now()]],
            ['user_id', 'metric_type', 'count', 'message_length',  'timestamp']
        )


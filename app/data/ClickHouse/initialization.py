import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(host='localhost', database='vpn_db_test')


def log_metric(user_id, metric_type, count=1, **kwargs):
    data = [user_id, metric_type, count, datetime.now()]
    columns = ['user_id', 'metric_type', 'count', 'timestamp']

    if 'response_time' in kwargs:
        data.append(kwargs['response_time'])
        columns.append('response_time')

    if 'message_length' in kwargs:
        data.append(kwargs['message_length'])
        columns.append('message_length')

    client.insert('bot_metrics', [data], column_names=columns)

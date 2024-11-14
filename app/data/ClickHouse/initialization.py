import clickhouse_connect
from app.data import config

client = clickhouse_connect.get_client(host=config.CH_HOST, database=config.CH_DB_NAME)


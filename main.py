from aiogram.utils import executor
from app.handlers import dp
from app_logging import logger


if __name__ == "__main__":
    logger.info("Запускаю программу")
    executor.start_polling(dp)
from aiogram.utils import executor


from app.handlers import dp
from app.loader import set_default_commands
from app_logging import logger


async def on_startup(dp):

    from app import middlewares
    middlewares.setup(dp)

    await set_default_commands(dp)


if __name__ == "__main__":
    logger.info("Запускаю программу")
    executor.start_polling(dp, on_startup=on_startup)
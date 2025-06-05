import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.config import get_config
from database import db_helper, Base
from handlers.commands_handler import commands_router
from handlers.admin_handler import admin_router
from aiogram.client.session.aiohttp import AiohttpSession
from middlewares.db import DbSessionMiddleware

config = get_config()
token = config.BOT_TOKEN


async def connect_db():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():

    session = AiohttpSession(timeout=30)
    bot = Bot(token=token, session=session)


    dp = Dispatcher(storage=MemoryStorage(), bot=bot)

    # Настройка middleware для работы с БД
    dp.update.middleware(DbSessionMiddleware(session_pool=db_helper.session_factory))

    dp.include_router(commands_router)
    dp.include_router(admin_router)

    try:
        await bot.get_me()
        logging.info("Бот успешно подключился к Telegram API")

        await connect_db()
        logging.info("Подключение к базе данных установлено")

        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка подключения: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
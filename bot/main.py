import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import TOKEN, ADMINS, CHANNEL_ID
from bot.handlers import user, admin, errors
from bot.services import console_logger


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    dp = Dispatcher()

    dp.include_router(errors.errors_router)
    dp.include_router(admin.admin_router)
    dp.include_router(user.user_router)

    await bot.delete_webhook(drop_pending_updates=True)

    console_logger.log_bot_start(
        token_loaded=bool(TOKEN),
        admins=ADMINS,
        channel_id=CHANNEL_ID
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        console_logger.log_bot_stop()
import traceback
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent

from bot.config import ADMINS

errors_router = Router()


@errors_router.error(F.update.message.as_("message"))
async def handle_errors(event: ErrorEvent, message: Message, bot: Bot):
    error_message = (
        f"❗️ **Произошла ошибка в чате с пользователем**\n\n"
        f"Пользователь: @{message.from_user.username} (ID: `{message.from_user.id}`)\n"
        f"Текст сообщения: `{message.text}`\n\n"
        f"Ошибка: `{event.exception}`\n\n"
        f"```\n{traceback.format_exc()}\n```"
    )

    print(f"Error processing message from {message.from_user.id}: {event.exception}")
    print(traceback.format_exc())

    for admin_id in ADMINS:
        try:
            if len(error_message) > 4096:
                error_message = error_message[:4090] + "\n...```"
            await bot.send_message(
                admin_id,
                error_message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение об ошибке админу {admin_id}: {e}")
import traceback
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent

from bot.config import ADMINS

errors_router = Router()

def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

@errors_router.error(F.update.message.as_("message"))
async def handle_errors(event: ErrorEvent, message: Message, bot: Bot):
    safe_username = escape_markdown_v2(message.from_user.username or "N/A")
    safe_message_text = escape_markdown_v2(message.text or "")
    safe_exception = escape_markdown_v2(str(event.exception))
    safe_traceback = escape_markdown_v2(traceback.format_exc())

    error_message = (
        f"❗️ *Произошла ошибка в чате с пользователем*\n\n"
        f"Пользователь: @{safe_username} \\(ID: `{message.from_user.id}`\\)\n"
        f"Текст сообщения: `{safe_message_text}`\n\n"
        f"Ошибка: `{safe_exception}`\n\n"
        f"```\n{safe_traceback}\n```"
    )
    if len(error_message) > 4096:
        cut_len = len(error_message) - 4090
        safe_traceback = traceback.format_exc()[:-cut_len]
        error_message = (
            f"❗️ *Произошла ошибка в чате с пользователем*\n\n"
            f"Пользователь: @{safe_username} \\(ID: `{message.from_user.id}`\\)\n"
            f"Текст сообщения: `{safe_message_text}`\n\n"
            f"Ошибка: `{safe_exception}`\n\n"
            f"```\n{safe_traceback}\n…```"
        )

    print(f"Error processing message from {message.from_user.id}: {event.exception}")
    print(traceback.format_exc())
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                error_message,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение об ошибке админу {admin_id}: {e}")
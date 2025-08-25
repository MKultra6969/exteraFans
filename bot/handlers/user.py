import re
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.config import ADMINS
from bot.services import filters, storage, console_logger
from bot.keyboards import inline
import html

user_router = Router()

PENDING_APPLICATIONS = {}

USERNAME_REGEX = re.compile(r'(@[a-zA-Z0-9_]{5,32})')

def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

@user_router.message(CommandStart(), F.chat.type == "private")
@user_router.message(Command("help"), F.chat.type == "private")
async def command_start_handler(message: Message):
    safe_full_name = html.escape(message.from_user.full_name)
    await message.answer(f"👋 <b>Привет, {safe_full_name}!</b>", parse_mode="HTML")

    guide_text = storage.get_guide_text()
    if guide_text:
        await message.answer(guide_text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        default_guide = (
            "<b>Как подать заявку:</b>\n\n"
            "Отправь мне сообщение в формате:\n"
            "<pre>Текст твоей заявки @твой_username доп. инфо</pre>\n\n"
            "<b>Пример:</b>\n"
            "<code>Legend: @mkultra6969 чпокает всех в рот</code>\n\n"
            "Заявка будет отправлена на рассмотрение."
        )
        await message.answer(default_guide, parse_mode="HTML")

@user_router.message(F.text, ~F.text.startswith('/'), F.chat.type == "private")
@user_router.edited_message(F.text, ~F.text.startswith('/'), F.chat.type == "private")
async def handle_user_application(message: Message, bot: Bot):
    user_id = message.from_user.id

    banned_users = storage.get_banned_users()
    if str(user_id) in banned_users:
        reason = banned_users[str(user_id)].get("reason", "Причина не указана.")
        await message.reply(f"❌ Вы были забанены и не можете подавать заявки.\n**Причина:** {reason}")
        return

    text = message.text

    banned_word = filters.check_for_banwords(text)
    if banned_word:
        await message.reply(f"❌ **Отказ.** В вашей заявке найдено запрещённое слово: `{banned_word}`")
        return

    match = USERNAME_REGEX.search(text)
    if not match:
        await message.reply("❌ **Неверный формат заявки.**\nУбедитесь, что в вашем сообщении присутствует ваш `@username`.")
        return

    username = match.group(1)
    parts = text.split(username)
    text_before = parts[0].strip()
    text_after = parts[1].strip()

    if not text_before:
        await message.reply("❌ **Неверный формат заявки.**\nПеред вашим `@username` должен быть какой-то текст.")
        return

    if len(text_after) > 25:
        await message.reply(f"❌ **Неверный формат заявки.**\nПосле вашего `@username` слишком много символов ({len(text_after)}/25).")
        return

    PENDING_APPLICATIONS[user_id] = {
        "text": text,
        "admin_messages": []
    }

    console_logger.log_new_application(message.from_user.full_name, user_id)

    admin_keyboard = inline.get_admin_approval_keyboard(user_id)
    admin_message_text = (
        f"❗️ **Новая заявка**\n\n"
        f"От: {message.from_user.full_name} (ID: `{user_id}`)\n\n"
        f"Текст заявки:\n`{text}`"
    )

    for admin_id in ADMINS:
        try:
            sent_message = await bot.send_message(
                chat_id=admin_id,
                text=admin_message_text,
                reply_markup=admin_keyboard,
                parse_mode="Markdown"
            )
            PENDING_APPLICATIONS[user_id]["admin_messages"].append(
                (admin_id, sent_message.message_id)
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение админу {admin_id}: {e}")

    await message.reply("✅ **Ваша заявка отправлена на рассмотрение.**")
from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from bot.config import ADMINS, CHANNEL_ID
from bot.services import storage, builder, channel_service, console_logger
from bot.handlers.user import PENDING_APPLICATIONS
import html

class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMINS

class AdminDeclineState(StatesGroup):
    waiting_for_reason = State()

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

async def _update_all_admin_messages(bot: Bot, user_id: int, new_text: str):
    app_data = PENDING_APPLICATIONS.get(user_id)
    if not app_data or not app_data.get("admin_messages"):
        return

    for chat_id, message_id in app_data["admin_messages"]:
        try:
            await bot.edit_message_text(
                text=new_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=None,
                parse_mode="Markdown"
            )
        except TelegramBadRequest as e:
            if "message to edit not found" in str(e):
                continue
            print(f"Не удалось отредактировать сообщение {message_id} в чате {chat_id}: {e}")

@admin_router.message(Command("help"))
async def admin_help_command(message: Message):
    admin_help_text = (
        "**Админ-панель | Доступные команды**\n\n"
        "**Управление инструкцией для пользователей (HTML-разметка):**\n"
        "• `/setguide [текст]` — Устанавливает текст инструкции, который видят пользователи после `/start`.\n"
        "• `/getguide` — Показывает текущий текст инструкции.\n"
        "• `/delguide` — Удаляет текст инструкции.\n\n"
        "**Управление контентом поста в канале (HTML-разметка):**\n"
        "• `/setcontent [текст]` — Устанавливает основной, редактируемый текст поста.\n"
        "• `/getcontent` — Показывает текущий текст для удобного копирования.\n"
        "• `/delcontent` — Полностью удаляет основной текст.\n\n"
        "**Управление бан-листом (слова):**\n"
        "• `/addban [слово]` — Добавляет слово в бан-лист.\n"
        "• `/listban` — Показывает весь бан-лист.\n\n"
        "**Управление банами пользователей:**\n"
        "• `/ban [id/@username] [причина]` — Банит пользователя и удаляет его из списка фанатов.\n"
        "• `/unban [id]` — Снимает бан с пользователя.\n"
        "• `/banlist` — Показывает список забаненных пользователей.\n\n"
        "**Прочее:**\n"
        "• `/cancel` — Отменяет текущее действие (например, ввод причины отказа)."
    )
    await message.answer(admin_help_text, parse_mode="Markdown")


@admin_router.callback_query(F.data.startswith("approve:"))
async def handle_approve_callback(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])

    # ИЗМЕНЕНИЕ: Получаем данные заявки, а не только текст
    app_data = PENDING_APPLICATIONS.get(user_id)
    if not app_data:
        await callback.message.edit_text(
            f"{callback.message.text}\n\n⚠️ **Ошибка:** Заявка не найдена (возможно, бот перезапускался). Попросите пользователя отправить ее повторно.")
        await callback.answer("⚠️ Заявка не найдена", show_alert=True)
        return

    original_text = app_data["text"]
    storage.add_fan(original_text)

    success, error = await channel_service.update_channel_post(bot)

    if not success:
        await callback.answer(f"⚠️ Ошибка при обновлении канала: {error}", show_alert=True)
        final_text = (
            f"{callback.message.text.split('Текст заявки:')[0]}"
            f"Текст заявки:\n`{original_text}`\n\n"
            f"✅ **Одобрено (локально)** админом {callback.from_user.full_name}\n"
            f"❗️ **НО:** Не удалось обновить пост в канале. Ошибка: {error}"
        )
        await _update_all_admin_messages(bot, user_id, final_text)
        PENDING_APPLICATIONS.pop(user_id, None)
        return

    console_logger.log_application_approved(callback.from_user.full_name, user_id)

    final_text = (
        f"{callback.message.text.split('Текст заявки:')[0]}"
        f"Текст заявки:\n`{original_text}`\n\n"
        f"✅ **Одобрено** админом {callback.from_user.full_name}"
    )
    await _update_all_admin_messages(bot, user_id, final_text)

    PENDING_APPLICATIONS.pop(user_id, None)

    try:
        await bot.send_message(user_id, "✅ Ваша заявка была одобрена и добавлена в список!")
    except Exception as e:
        print(f"Не удалось уведомить пользователя {user_id} об одобрении: {e}")
    await callback.answer("✅ Заявка одобрена и пост в канале обновлен!")


@admin_router.callback_query(F.data.startswith("decline:"))
async def handle_decline_callback(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])

    if user_id not in PENDING_APPLICATIONS:
        await callback.message.edit_text(f"{callback.message.text}\n\n⚠️ **Ошибка:** Заявка не найдена (возможно, бот перезапускался).")
        await callback.answer("⚠️ Заявка не найдена", show_alert=True)
        return

    await state.update_data(
        user_to_notify=user_id,
        original_admin_message_text=callback.message.text
    )
    await state.set_state(AdminDeclineState.waiting_for_reason)
    await callback.message.edit_text(f"{callback.message.text}\n\n✍️ **Введите причину отказа...** (можно отменить командой /cancel)")
    await callback.answer("Введите причину отказа")



@admin_router.message(Command("cancel"))
async def cancel_decline(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действие отменено.")


@admin_router.message(AdminDeclineState.waiting_for_reason)
async def handle_decline_reason(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("user_to_notify")
    reason = message.text
    original_admin_message_text = data.get("original_admin_message_text")

    console_logger.log_application_declined(message.from_user.full_name, user_id, reason)

    final_text = (
        f"{original_admin_message_text}\n\n"
        f"❌ **Отклонено** админом {message.from_user.full_name}\n"
        f"**Причина:** {reason}"
    )
    await _update_all_admin_messages(bot, user_id, final_text)

    PENDING_APPLICATIONS.pop(user_id, None)

    try:
        await bot.send_message(user_id, f"❌ Ваша заявка была отклонена.\n\n**Причина:** {reason}")
    except Exception as e:
        print(f"Не удалось уведомить пользователя {user_id} об отклонении: {e}")

    await message.reply(f"Причина отказа отправлена пользователю.")
    await state.clear()


@admin_router.message(Command("addban"))
async def add_banword_command(message: Message, command: Command):
    if not command.args:
        await message.reply("Неверный формат. Используйте: `/addban слово`")
        return
    word = command.args.strip()
    if storage.add_banword(word):
        console_logger.log_banword_added(message.from_user.full_name, word)
        await message.reply(f"✅ Слово `{word}` добавлено в бан-лист.")
    else:
        await message.reply(f"⚠️ Слово `{word}` уже было в бан-листе.")


@admin_router.message(Command("listban"))
async def list_banwords_command(message: Message):
    banwords = storage.get_banwords()
    if not banwords:
        await message.reply("🚫 Список запрещённых слов пуст.")
        return
    text = "📝 **Список запрещённых слов:**\n\n" + "\n".join([f"• `{word}`" for word in banwords])
    await message.reply(text)


@admin_router.message(Command("setcontent"))
@admin_router.edited_message(Command("setcontent"))
async def set_content_command(message: Message, bot: Bot):
    if message.entities and message.entities[0].type == "bot_command":
        command_len = message.entities[0].length
        content_text = message.html_text[command_len:].strip()
    else:
        content_text = message.html_text.replace("/setcontent", "", 1).strip()

    if not content_text:
        await message.reply(
            "Неверный формат. Используйте: `/setcontent Ваш текст...`\n"
            "Текст может быть многострочным и содержать форматирование."
        )
        return

    storage.set_content_text(content_text)
    console_logger.log_content_updated(message.from_user.full_name)
    await message.reply("✅ Основной текст поста сохранен. Начинаю обновление в канале...")

    success, error = await channel_service.update_channel_post(bot)
    if success:
        await message.answer("✅ Пост в канале успешно обновлен.")
    else:
        await message.answer(f"⚠️ **Ошибка:** Не удалось обновить пост в канале. {error}")


@admin_router.message(Command("getcontent"))
async def get_content_command(message: Message):
    content = storage.get_content_text()
    if content:
        await message.answer(f"Текущий текст поста:\n\n`{content}`")
    else:
        await message.answer("Основной текст поста пока не задан.")


@admin_router.message(Command("delcontent"))
async def delete_content_command(message: Message, bot: Bot):
    storage.set_content_text("")
    console_logger.log_content_updated(message.from_user.full_name)
    await message.reply("✅ Основной текст поста удален. Начинаю обновление в канале...")

    success, error = await channel_service.update_channel_post(bot)
    if success:
        await message.answer("✅ Пост в канале успешно обновлен.")
    else:
        await message.answer(f"⚠️ **Ошибка:** Не удалось обновить пост в канале. {error}")


@admin_router.message(Command("ban"))
async def ban_user_command(message: Message, command: Command, bot: Bot):
    if not command.args:
        await message.reply("Неверный формат. Используйте: `/ban @username/id [причина]`")
        return

    args = command.args.split(maxsplit=1)
    target_str = args[0]
    reason = args[1] if len(args) > 1 else "Без причины"

    target_id = None
    target_username = None

    if target_str.isdigit():
        target_id = int(target_str)
    elif target_str.startswith('@'):
        target_username = target_str
        for uid, text in PENDING_APPLICATIONS.items():
            if target_username in text:
                target_id = uid
                break
    else:
        await message.reply("Неверный формат цели. Укажите ID пользователя или его @username.")
        return

    if not target_id:
        await message.reply(f"Не удалось определить ID для `{target_str}`. "
                            f"Бан по юзернейму возможен только для пользователей с активной заявкой. "
                            f"Попробуйте забанить по ID.")
        return

    if target_id in ADMINS:
        await message.reply("Нельзя забанить администратора.")
        return

    storage.ban_user(user_id=target_id, reason=reason, admin_id=message.from_user.id)
    console_logger.log_user_banned(message.from_user.full_name, target_id, reason)
    await message.reply(f"✅ Пользователь с ID `{target_id}` забанен.\nПричина: {reason}")

    fan_removed = False
    text_to_find = target_username if target_username else str(target_id)

    if storage.remove_fan_by_text_part(text_to_find):
        fan_removed = True

    if fan_removed:
        await message.answer(
            f"🧹 Пользователь `{text_to_find}` найден в списке фанатов. Начинаю обновление поста в канале...")
        success, error = await channel_service.update_channel_post(bot)
        if success:
            await message.answer("✅ Пост в канале успешно обновлен.")
        else:
            await message.answer(f"⚠️ **Ошибка:** Не удалось обновить пост в канале. {error}")
    elif target_username:
        await message.answer(f"ℹ️ Пользователь `{target_username}` не найден в текущем списке фанатов.")


@admin_router.message(Command("unban"))
async def unban_user_command(message: Message, command: Command):
    if not command.args or not command.args.strip().isdigit():
        await message.reply("Неверный формат. Используйте: `/unban id_пользователя`")
        return

    user_id = int(command.args.strip())

    if storage.unban_user(user_id):
        console_logger.log_user_unbanned(message.from_user.full_name, user_id)
        await message.reply(f"✅ Пользователь с ID `{user_id}` разбанен.")
    else:
        await message.reply(f"⚠️ Пользователь с ID `{user_id}` не найден в списке забаненных.")


@admin_router.message(Command("banlist"))
async def banlist_command(message: Message):
    banned_users = storage.get_banned_users()
    if not banned_users:
        await message.reply("🚫 Список забаненных пользователей пуст.")
        return

    text = "📝 **Список забаненных пользователей:**\n\n"
    for user_id, info in banned_users.items():
        text += (
            f"• **ID:** `{user_id}`\n"
            f"  **Причина:** {info.get('reason', 'н/у')}\n"
            f"  **Забанил:** `{info.get('banned_by', 'н/у')}`\n\n"
        )

    if len(text) > 4096:
        await message.reply("Слишком большой список, будет выведен в нескольких сообщениях.")
        for i in range(0, len(text), 4096):
            await message.answer(text[i:i + 4096])
    else:
        await message.reply(text)

@admin_router.message(Command("setguide"))
@admin_router.edited_message(Command("setguide"))
async def set_guide_command(message: Message):
    if message.entities and message.entities[0].type == "bot_command":
        command_len = message.entities[0].length
        guide_text = message.html_text[command_len:].strip()
    else:
        guide_text = message.html_text.replace("/setguide", "", 1).strip()

    if not guide_text:
        await message.reply(
            "Неверный формат. Используйте: `/setguide Ваш текст...`\n"
            "Текст может быть многострочным и содержать HTML-форматирование."
        )
        return

    storage.set_guide_text(guide_text)
    console_logger.log_guide_updated(message.from_user.full_name)
    await message.reply("✅ Инструкция для пользователей сохранена.")


@admin_router.message(Command("getguide"))
async def get_guide_command(message: Message):
    guide = storage.get_guide_text()
    if guide:
        await message.answer("Текущий текст инструкции:")
        await message.answer(guide, parse_mode="HTML")
        await message.answer("Для копирования:")
        await message.answer(f"<code>{html.escape(guide)}</code>", parse_mode="HTML")
    else:
        await message.answer("Инструкция для пользователей пока не задана.")


@admin_router.message(Command("delguide"))
async def delete_guide_command(message: Message):
    storage.set_guide_text("")
    console_logger.log_guide_updated(message.from_user.full_name)
    await message.reply("✅ Инструкция для пользователей удалена.")
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.config import CHANNEL_ID
from bot.services import storage, builder


async def update_channel_post(bot: Bot) -> tuple[bool, str | None]:

    try:
        content_part = storage.get_content_text() or ""
        all_fans = storage.get_fans()
        fan_chunks = builder.build_fan_list_messages(all_fans)

        final_posts = []
        if not fan_chunks and content_part:
            final_posts.append(content_part)
        elif fan_chunks:
            first_chunk = fan_chunks[0]
            separator = "\n\n" if content_part else ""
            final_posts.append(content_part + separator + first_chunk)
            final_posts.extend(fan_chunks[1:])

        old_post_ids = storage.get_posts()
        new_post_ids = []

        for i, text_chunk in enumerate(final_posts):
            if i < len(old_post_ids):
                post_id = old_post_ids[i]
                try:
                    await bot.edit_message_text(text=text_chunk,
                                                chat_id=CHANNEL_ID,
                                                message_id=post_id,
                                                parse_mode="HTML",
                                                disable_web_page_preview=True)
                    new_post_ids.append(post_id)
                except TelegramBadRequest as e:
                    print(f"Не удалось отредактировать сообщение {post_id}: {e}. Создаю новое.")
                    new_msg = await bot.send_message(chat_id=CHANNEL_ID, text=text_chunk, parse_mode="HTML",
                                                     disable_web_page_preview=True)
                    new_post_ids.append(new_msg.message_id)
            else:
                new_msg = await bot.send_message(chat_id=CHANNEL_ID, text=text_chunk, parse_mode="HTML",
                                                 disable_web_page_preview=True)
                new_post_ids.append(new_msg.message_id)

        if len(old_post_ids) > len(new_post_ids):
            for post_id in old_post_ids[len(new_post_ids):]:
                try:
                    await bot.delete_message(chat_id=CHANNEL_ID, message_id=post_id)
                except TelegramBadRequest as e:
                    print(f"Не удалось удалить сообщение {post_id}: {e}")

        if not final_posts and old_post_ids:
            for post_id in old_post_ids:
                try:
                    await bot.delete_message(chat_id=CHANNEL_ID, message_id=post_id)
                except TelegramBadRequest as e:
                    print(f"Не удалось удалить сообщение {post_id}: {e}")

        storage.update_posts(new_post_ids)
        return True, None

    except Exception as e:
        error_message = f"Критическая ошибка при обновлении канала: {e}"
        print(error_message)
        return False, str(e)
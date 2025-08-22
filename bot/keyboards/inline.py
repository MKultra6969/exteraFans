from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="✅ Одобрить",
            callback_data=f"approve:{user_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"decline:{user_id}"
        )
    )

    builder.adjust(2)

    return builder.as_markup()
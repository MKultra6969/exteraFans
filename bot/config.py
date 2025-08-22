import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS")
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID")


ADMINS = []
if ADMIN_IDS_RAW:
    try:
        ADMINS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_RAW.split(",")]
    except ValueError:
        print("ОШИБКА: Не удалось обработать ADMIN_IDS. Убедитесь, что это числа, разделенные запятой.")

CHANNEL_ID = None
if CHANNEL_ID_RAW:
    try:
        CHANNEL_ID = int(CHANNEL_ID_RAW)
    except ValueError:
        print("ОШИБКА: Не удалось обработать CHANNEL_ID. Убедитесь, что это число.")


if not all([TOKEN, ADMINS, CHANNEL_ID]):
    raise SystemExit("КРИТИЧЕСКАЯ ОШИБКА: Одна или несколько обязательных переменных окружения не загружены. Бот не может быть запущен.")
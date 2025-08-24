from datetime import datetime

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_MAGENTA = '\033[95m'

def _print_header(title, color):
    print("\n" + color + Colors.BOLD + "╔" + "═" * (len(title) + 2) + "╗" + Colors.RESET, flush=True)
    print(color + Colors.BOLD + "║ " + title + " ║" + Colors.RESET, flush=True)
    print(color + Colors.BOLD + "╚" + "═" * (len(title) + 2) + "╝" + Colors.RESET, flush=True)

def log_new_application(user_name: str, user_id: int):
    _print_header("📬 Новая заявка", Colors.CYAN)
    print(f"{Colors.CYAN}│{Colors.RESET} От пользователя: {Colors.BOLD}{user_name}{Colors.RESET}", flush=True)
    print(f"{Colors.CYAN}╰─> {Colors.RESET}ID: {Colors.YELLOW}{user_id}{Colors.RESET}", flush=True)

def log_application_approved(admin_name: str, user_id: int):
    _print_header("✅ Заявка одобрена", Colors.BRIGHT_GREEN)
    print(f"{Colors.BRIGHT_GREEN}│{Colors.RESET} Админ: {Colors.BOLD}{admin_name}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_GREEN}╰─> {Colors.RESET}Одобрен пользователь с ID: {Colors.YELLOW}{user_id}{Colors.RESET}", flush=True)

def log_application_declined(admin_name: str, user_id: int, reason: str):
    _print_header("❌ Заявка отклонена", Colors.BRIGHT_RED)
    print(f"{Colors.BRIGHT_RED}│{Colors.RESET} Админ: {Colors.BOLD}{admin_name}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_RED}│{Colors.RESET} Отклонен пользователь с ID: {Colors.YELLOW}{user_id}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_RED}╰─> {Colors.RESET}Причина: {Colors.YELLOW}{reason}{Colors.RESET}", flush=True)

def log_user_banned(admin_name: str, target_id: int, reason: str):
    _print_header("🚫 Пользователь забанен", Colors.BRIGHT_RED)
    print(f"{Colors.BRIGHT_RED}│{Colors.RESET} Админ: {Colors.BOLD}{admin_name}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_RED}│{Colors.RESET} Забанен ID: {Colors.YELLOW}{target_id}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_RED}╰─> {Colors.RESET}Причина: {Colors.YELLOW}{reason}{Colors.RESET}", flush=True)

def log_user_unbanned(admin_name: str, target_id: int):
    _print_header("🔓 Пользователь разбанен", Colors.YELLOW)
    print(f"{Colors.YELLOW}│{Colors.RESET} Админ: {Colors.BOLD}{admin_name}{Colors.RESET}", flush=True)
    print(f"{Colors.YELLOW}╰─> {Colors.RESET}Разбанен ID: {Colors.GREEN}{target_id}{Colors.RESET}", flush=True)

def log_banword_added(admin_name: str, word: str):
    _print_header("✏️ Новое бан-слово", Colors.MAGENTA)
    print(f"{Colors.MAGENTA}│{Colors.RESET} Админ: {Colors.BOLD}{admin_name}{Colors.RESET}", flush=True)
    print(f"{Colors.MAGENTA}╰─> {Colors.RESET}Слово: {Colors.YELLOW}`{word}`{Colors.RESET}", flush=True)

def log_content_updated(admin_name: str):
    _print_header("📝 Контент обновлен", Colors.BLUE)
    print(f"{Colors.BLUE}╰─> {Colors.RESET}Админ {Colors.BOLD}{admin_name}{Colors.RESET} изменил основной текст поста.", flush=True)


def log_bot_start(token_loaded: bool, admins: list, channel_id: int):
    logo = r"""
+═════════════════════════════════════════════════════════════════════════+
║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
║                                                                         ║
+═════════════════════════════════════════════════════════════════════════+
║                               MKultra69                                 ║
+═════════════════════════════════════════════════════════════════════════+
"""
    print(f"{Colors.BRIGHT_MAGENTA}{logo}{Colors.RESET}")

    _print_header("🚀 Бот успешно запущен", Colors.BRIGHT_GREEN)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.BRIGHT_GREEN}│{Colors.RESET} Время запуска: {Colors.YELLOW}{timestamp}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_GREEN}├─{Colors.RESET} Токен: {'✅ Загружен' if token_loaded else '❌ НЕ НАЙДЕН'}", flush=True)
    print(f"{Colors.BRIGHT_GREEN}├─{Colors.RESET} ID Админов: {Colors.CYAN}{admins}{Colors.RESET}", flush=True)
    print(f"{Colors.BRIGHT_GREEN}╰─> {Colors.RESET}ID Канала: {Colors.CYAN}{channel_id}{Colors.RESET}", flush=True)
    print(f"\n{Colors.GREEN}✅ Готов к приему заявок!{Colors.RESET}", flush=True)

def log_bot_stop():
    _print_header("🛑 Бот остановлен", Colors.YELLOW)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.YELLOW}╰─> {Colors.RESET}Завершение работы... До встречи! ({timestamp}){Colors.RESET}\n", flush=True)
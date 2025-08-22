import os
import subprocess
import sys

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(title, color=Colors.BLUE):
    print(f"\n{color}{Colors.BOLD}--- {title.upper()} ---{Colors.RESET}")


def run_command(command, stream_output=False):
    try:
        if stream_output:
            print(f"{Colors.YELLOW}Вывод логов (нажмите Ctrl+C для выхода)...{Colors.RESET}")
            subprocess.run(command, check=False)
            return True

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Успешно!{Colors.RESET}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"{Colors.RED}❌ Ошибка!{Colors.RESET}")
            print(f"{Colors.RED}{result.stderr}{Colors.RESET}")
            return False

    except FileNotFoundError:
        print(f"{Colors.RED}❌ Критическая ошибка: `docker-compose` не найден.{Colors.RESET}")
        print("   Убедитесь, что Docker и Docker Compose установлены и доступны в PATH.")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🚫 Операция прервана.{Colors.RESET}")
        return False


def check_env_file():
    if os.path.exists(".env"):
        return True

    print_header("ПРОВЕРКА КОНФИГУРАЦИИ", Colors.YELLOW)
    print(f"{Colors.YELLOW}⚠️ Файл конфигурации `.env` не найден.{Colors.RESET}")

    try:
        answer = input("   Хотите создать его из примера (`.env.exemple`)? [Y/n]: ").lower().strip()
    except EOFError:
        answer = 'n'

    if answer in ('y', 'yes', ''):
        try:
            with open(".env.exemple", "r", encoding="utf-8") as f_example, \
                    open(".env", "w", encoding="utf-8") as f_env:
                f_env.write(f_example.read())

            print(f"\n{Colors.GREEN}✅ Файл `.env` успешно создан.{Colors.RESET}")
            print(
                f"{Colors.BOLD}   Теперь откройте его, впишите свои данные (BOT_TOKEN и т.д.), сохраните и запустите команду `start` снова.{Colors.RESET}")
            print(f"   Путь к файлу: {os.path.abspath('.env')}")
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Ошибка: не найден файл `.env.exemple` для создания копии.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}🚫 Запуск невозможен без файла `.env`.{Colors.RESET}")

    return False


def print_help():
    print_header("СПРАВКА ПО УПРАВЛЕНИЮ БОТОМ", Colors.GREEN)
    print(f"Используйте: {Colors.BOLD}python manage.py [команда]{Colors.RESET}\n")
    print("Доступные команды:")
    print(f"  {Colors.GREEN}start{Colors.RESET}   - Собрать и запустить бота в фоновом режиме.")
    print(f"  {Colors.YELLOW}stop{Colors.RESET}    - Остановить и удалить контейнер бота.")
    print(f"  {Colors.BLUE}restart{Colors.RESET} - Перезапустить бота.")
    print(f"  {Colors.YELLOW}logs{Colors.RESET}    - Показать логи (журнал работы) бота.")
    print(f"  {Colors.BLUE}status{Colors.RESET}  - Показать статус контейнера.")
    print(f"  {Colors.BOLD}help{Colors.RESET}    - Показать это сообщение.")
    print("\nПример:")
    print(f"  {Colors.BOLD}python manage.py start{Colors.RESET}")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "start":
        print_header("ЗАПУСК БОТА")
        if check_env_file():
            print("Собираю образ и запускаю контейнер...")
            run_command(["docker-compose", "up", "--build", "-d"])

    elif command == "stop":
        print_header("ОСТАНОВКА БОТА")
        print("Останавливаю и удаляю контейнер...")
        run_command(["docker-compose", "down"])

    elif command == "restart":
        print_header("ПЕРЕЗАПУСК БОТА")
        print("1/2: Останавливаю контейнер...")
        if run_command(["docker-compose", "down"]):
            print("\n2/2: Запускаю контейнер заново...")
            run_command(["docker-compose", "up", "--build", "-d"])

    elif command == "logs":
        print_header("ЛОГИ БОТА")
        run_command(["docker-compose", "logs", "-f", "--tail=100"], stream_output=True)

    elif command == "status":
        print_header("СТАТУС КОНТЕЙНЕРА")
        run_command(["docker-compose", "ps"])

    elif command in ("help", "-h", "--help"):
        print_help()

    else:
        print(f"{Colors.RED}Неизвестная команда: '{command}'{Colors.RESET}")
        print_help()


if __name__ == "__main__":
    main()
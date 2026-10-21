# main.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.controller import RegistrationController
from src.db_repository import RegistrationRepository
from src.notifier import EmailNotifier
from src.user_interface import ConsoleUserInterface


def main():
    ui = ConsoleUserInterface()
    db = RegistrationRepository("users.db")  # файл рядом с main.py
    notifier = EmailNotifier()

    controller = RegistrationController(ui, db, notifier)

    print("=" * 60)
    print("  РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)

    while True:
        try:
            result, message = controller.process_registration()

            print("\n--- РЕЗУЛЬТАТ ---")
            if result:
                print("✅ Регистрация успешна!")

                # ВЫВОДИМ СПИСОК ВСЕХ ЗАРЕГИСТРИРОВАННЫХ
                users = db.get_successful_users()
                print(f"👥 Всего зарегистрировано: {len(users)}")
                print("Список пользователей:")
                for i, login in enumerate(users, 1):
                    print(f"  {i}. {login}")

            else:
                print(f"❌ Регистрация отклонена: {message}")

            if notifier.sent:
                print(f"📧 На сервер отправлено: {notifier.sent[-1]}")

            print()

            again = input("Зарегистрировать ещё одного пользователя? (y/n): ").strip().lower()
            if again != "y":
                break

        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

    db.close()
    print("Программа завершена. Данные сохранены в users.db")


if __name__ == "__main__":
    main()
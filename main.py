import logging
import sys

from setup_logging import setlog
from validator import validate_registration

def main():
    setlog()


    while True:
        login = input("Введите логин(Если нужно выйти пиши <<Выход>>): ")
        if login == "Выход": break
        pwd = input("Введите пароль: ")
        confirm = input("Подтверидите парль: ")

        result, message = validate_registration(login, pwd, confirm)
        logging.info(f"Результат {result}, сообщение: {message!r}")
if __name__ == "__main__":
    main()


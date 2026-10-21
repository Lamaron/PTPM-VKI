from src.db_repository import RegistrationRepository
from src.notifier import AbstractNotifier
from src.user_interface import AbstractUserInterface
from src.validator import RegistrationValidator


class RegistrationController:

    def __init__(self,
                 ui: AbstractUserInterface,
                 db: RegistrationRepository,
                 notifier: AbstractNotifier,
                 validator: RegistrationValidator | None = None):
        self.ui = ui
        self.db = db
        self.notifier = notifier
        self.validator = validator or RegistrationValidator()

    def process_registration(self) -> tuple:
        login = self.ui.get_input("Логин: ")
        password = self.ui.get_input("Пароль: ")
        confirm = self.ui.get_input("Подтверждение пароля: ")

        cached = self.db.get(login, password, confirm)
        if cached is not None:
            result = cached["result"]
            message = cached["message"]
            source = "cache"
        else:
            result, message = self.validator.validate(login, password, confirm)
            self.db.add(login, password, confirm, result, message)
            source = "computed"

        text = f"[{source}] login={login!r}, result={result}, message={message!r}"
        self.notifier.send(text)

        return result, message
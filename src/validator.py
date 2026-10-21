
import re

BLACKLIST = {
    "admin", "root", "user", "test", "guest",
    "superuser", "moderator", "administrator", "support", "manager",
}
BLACKLIST_LOWER = {login.lower() for login in BLACKLIST}

PHONE_RE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
LOGIN_STR_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")
PWD_ALLOWED_RE = re.compile(r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]+$")
PWD_UPPER_RE = re.compile(r"[А-ЯЁ]")
PWD_LOWER_RE = re.compile(r"[а-яё]")
PWD_DIGIT_RE = re.compile(r"\d")
PWD_SPECIAL_RE = re.compile(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]")


class RegistrationValidator:

    def validate(self, login, password, confirm) -> tuple:
        err = self._validate_login(login)
        if err:
            return False, err

        err = self._validate_password(password)
        if err:
            return False, err

        err = self._validate_confirm(password, confirm)
        if err:
            return False, err

        return True, ""

    @staticmethod
    def _validate_login(login) -> str:
        if login is None:
            return "Логин не может быть пустым."
        if not isinstance(login, str):
            return "Логин должен быть строкой."
        if login == "":
            return "Логин не может быть пустым."

        if login.startswith("+"):
            if not PHONE_RE.match(login):
                return "Некорректный формат телефона. Ожидается +x-xxx-xxx-xxxx."
            return ""

        if "@" in login:
            if not EMAIL_RE.match(login):
                return "Некорректный формат email."
            if login.lower() in BLACKLIST_LOWER:
                return "Такой логин запрещён (чёрный список)."
            return ""

        if not LOGIN_STR_RE.match(login):
            if len(login) < 5:
                return "Логин-строка должен содержать минимум 5 символов."
            return "Логин-строка может содержать только латиницу, цифры и '_'."

        if login.lower() in BLACKLIST_LOWER:
            return "Такой логин запрещён (чёрный список)."

        return ""

    @staticmethod
    def _validate_password(password) -> str:
        if password is None:
            return "Пароль не может быть пустым."
        if not isinstance(password, str):
            return "Пароль должен быть строкой."
        if password == "":
            return "Пароль не может быть пустым."
        if len(password) < 7:
            return "Пароль должен содержать минимум 7 символов."
        if not PWD_ALLOWED_RE.match(password):
            return "Пароль может содержать только кириллицу, цифры и спецсимволы."
        if not PWD_UPPER_RE.search(password):
            return "Пароль должен содержать хотя бы одну заглавную букву кириллицы."
        if not PWD_LOWER_RE.search(password):
            return "Пароль должен содержать хотя бы одну строчную букву кириллицы."
        if not PWD_DIGIT_RE.search(password):
            return "Пароль должен содержать хотя бы одну цифру."
        if not PWD_SPECIAL_RE.search(password):
            return "Пароль должен содержать хотя бы один спецсимвол."
        return ""

    @staticmethod
    def _validate_confirm(password, confirm) -> str:
        if confirm is None or confirm == "":
            return "Подтверждение пароля не может быть пустым."
        if not isinstance(confirm, str):
            return "Пароль и подтверждение пароля не совпадают."
        if password != confirm:
            return "Пароль и подтверждение пароля не совпадают."
        return ""
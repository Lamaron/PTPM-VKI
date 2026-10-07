# src/my_project.py

import hashlib
import logging
import re

BLACKLIST = {
    "admin", "root", "user", "test", "guest",
    "superuser", "moderator", "administrator", "support", "manager",
}
BLACKLIST_LOWER = {login.lower() for login in BLACKLIST}


def mask_password(password) -> str:
    if password is None:
        return "pwd_<none>"
    if not isinstance(password, str):
        password = str(password)
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return f"pwd_{digest[:12]}"


MSG_OK = ""
MSG_LOGIN_EMPTY = "Логин не может быть пустым."
MSG_LOGIN_TYPE = "Логин должен быть строкой."
MSG_PHONE_INVALID = "Некорректный формат телефона. Ожидается +x-xxx-xxx-xxxx."
MSG_EMAIL_INVALID = "Некорректный формат email."
MSG_LOGIN_TOO_SHORT = "Логин-строка должен содержать минимум 5 символов."
MSG_LOGIN_CHARS = "Логин-строка может содержать только латиницу, цифры и '_'."
MSG_LOGIN_BLACKLISTED = "Такой логин запрещён (чёрный список)."
MSG_PWD_EMPTY = "Пароль не может быть пустым."
MSG_PWD_TYPE = "Пароль должен быть строкой."
MSG_PWD_TOO_SHORT = "Пароль должен содержать минимум 7 символов."
MSG_PWD_NO_UPPER = "Пароль должен содержать хотя бы одну заглавную букву кириллицы."
MSG_PWD_NO_LOWER = "Пароль должен содержать хотя бы одну строчную букву кириллицы."
MSG_PWD_NO_DIGIT = "Пароль должен содержать хотя бы одну цифру."
MSG_PWD_NO_SPECIAL = "Пароль должен содержать хотя бы один спецсимвол."
MSG_PWD_FORBIDDEN_CHARS = "Пароль может содержать только кириллицу, цифры и спецсимволы."
MSG_CONFIRM_EMPTY = "Подтверждение пароля не может быть пустым."
MSG_CONFIRM_MISMATCH = "Пароль и подтверждение пароля не совпадают."

PHONE_RE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
LOGIN_STR_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")
PWD_ALLOWED_RE = re.compile(r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]+$")
PWD_UPPER_RE = re.compile(r"[А-ЯЁ]")
PWD_LOWER_RE = re.compile(r"[а-яё]")
PWD_DIGIT_RE = re.compile(r"\d")
PWD_SPECIAL_RE = re.compile(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~№]")


def validate_login(login) -> str:
    if login is None:
        return MSG_LOGIN_EMPTY
    if not isinstance(login, str):
        return MSG_LOGIN_TYPE
    if login == "":
        return MSG_LOGIN_EMPTY
    if login.startswith("+"):
        if not PHONE_RE.match(login):
            return MSG_PHONE_INVALID
        return MSG_OK
    if "@" in login:
        if not EMAIL_RE.match(login):
            return MSG_EMAIL_INVALID
        if login.lower() in BLACKLIST_LOWER:
            return MSG_LOGIN_BLACKLISTED
        return MSG_OK
    if not LOGIN_STR_RE.match(login):
        if len(login) < 5:
            return MSG_LOGIN_TOO_SHORT
        return MSG_LOGIN_CHARS
    if login.lower() in BLACKLIST_LOWER:
        return MSG_LOGIN_BLACKLISTED
    return MSG_OK


def validate_password(password) -> str:
    if password is None:
        return MSG_PWD_EMPTY
    if not isinstance(password, str):
        return MSG_PWD_TYPE
    if password == "":
        return MSG_PWD_EMPTY
    if len(password) < 7:
        return MSG_PWD_TOO_SHORT
    if not PWD_ALLOWED_RE.match(password):
        return MSG_PWD_FORBIDDEN_CHARS
    if not PWD_UPPER_RE.search(password):
        return MSG_PWD_NO_UPPER
    if not PWD_LOWER_RE.search(password):
        return MSG_PWD_NO_LOWER
    if not PWD_DIGIT_RE.search(password):
        return MSG_PWD_NO_DIGIT
    if not PWD_SPECIAL_RE.search(password):
        return MSG_PWD_NO_SPECIAL
    return MSG_OK


def validate_confirm(password, confirm) -> str:
    if confirm is None or confirm == "":
        return MSG_CONFIRM_EMPTY
    if not isinstance(confirm, str):
        return MSG_CONFIRM_MISMATCH
    if password != confirm:
        return MSG_CONFIRM_MISMATCH
    return MSG_OK


def validate_registration(login, password, confirm):
    try:
        err = validate_login(login)
        if err:
            return False, err
        err = validate_password(password)
        if err:
            return False, err
        err = validate_confirm(password, confirm)
        if err:
            return False, err
        return True, MSG_OK
    except Exception:
        return False, "Внутренняя ошибка валидации."
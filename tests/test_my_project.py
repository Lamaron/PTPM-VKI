import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from my_project import (
    validate_login, validate_password, validate_confirm, validate_registration,
    mask_password,
    MSG_OK, MSG_LOGIN_EMPTY, MSG_LOGIN_TYPE, MSG_PHONE_INVALID, MSG_EMAIL_INVALID,
    MSG_LOGIN_TOO_SHORT, MSG_LOGIN_CHARS, MSG_LOGIN_BLACKLISTED,
    MSG_PWD_EMPTY, MSG_PWD_TYPE, MSG_PWD_TOO_SHORT, MSG_PWD_NO_UPPER,
    MSG_PWD_NO_LOWER, MSG_PWD_NO_DIGIT, MSG_PWD_NO_SPECIAL, MSG_PWD_FORBIDDEN_CHARS,
    MSG_CONFIRM_EMPTY, MSG_CONFIRM_MISMATCH,
)


class TestValidateLogin(unittest.TestCase):

    def test_valid_simple_login(self):
        self.assertEqual(validate_login("john_doe"), MSG_OK)

    def test_valid_login_min_length(self):
        self.assertEqual(validate_login("abcde"), MSG_OK)

    def test_valid_phone_login(self):
        self.assertEqual(validate_login("+7-999-123-4567"), MSG_OK)

    def test_valid_email_login(self):
        self.assertEqual(validate_login("user@example.com"), MSG_OK)

    def test_login_none_returns_empty_message(self):
        self.assertEqual(validate_login(None), MSG_LOGIN_EMPTY)

    def test_login_empty_string(self):
        self.assertEqual(validate_login(""), MSG_LOGIN_EMPTY)

    def test_login_non_string_type(self):
        self.assertEqual(validate_login(12345), MSG_LOGIN_TYPE)

    def test_login_too_short(self):
        self.assertEqual(validate_login("ab"), MSG_LOGIN_TOO_SHORT)

    def test_login_forbidden_characters(self):
        self.assertEqual(validate_login("user-name!"), MSG_LOGIN_CHARS)

    def test_login_in_blacklist(self):
        self.assertEqual(validate_login("admin"), MSG_LOGIN_BLACKLISTED)

    def test_login_blacklist_case_insensitive(self):
        self.assertEqual(validate_login("ADMIN"), MSG_LOGIN_BLACKLISTED)

    def test_invalid_phone_format(self):
        self.assertEqual(validate_login("+7-99-123-4567"), MSG_PHONE_INVALID)

    def test_invalid_email_format(self):
        self.assertEqual(validate_login("user@bad"), MSG_EMAIL_INVALID)


class TestValidatePassword(unittest.TestCase):

    def test_valid_password(self):
        self.assertEqual(validate_password("Пароль1!"), MSG_OK)

    def test_password_none(self):
        self.assertEqual(validate_password(None), MSG_PWD_EMPTY)

    def test_password_empty(self):
        self.assertEqual(validate_password(""), MSG_PWD_EMPTY)

    def test_password_non_string(self):
        self.assertEqual(validate_password(1234567), MSG_PWD_TYPE)

    def test_password_too_short(self):
        self.assertEqual(validate_password("П1!"), MSG_PWD_TOO_SHORT)

    def test_password_no_upper(self):
        self.assertEqual(validate_password("пароль1!"), MSG_PWD_NO_UPPER)

    def test_password_no_lower(self):
        self.assertEqual(validate_password("ПАРОЛЬ1!"), MSG_PWD_NO_LOWER)

    def test_password_no_digit(self):
        self.assertEqual(validate_password("Пароль!!"), MSG_PWD_NO_DIGIT)

    def test_password_no_special(self):
        self.assertEqual(validate_password("Пароль11"), MSG_PWD_NO_SPECIAL)

    def test_password_latin_forbidden(self):
        self.assertEqual(validate_password("Password1!"), MSG_PWD_FORBIDDEN_CHARS)


class TestValidateConfirm(unittest.TestCase):

    def test_confirm_matches(self):
        self.assertEqual(validate_confirm("Пароль1!", "Пароль1!"), MSG_OK)

    def test_confirm_empty(self):
        self.assertEqual(validate_confirm("Пароль1!", ""), MSG_CONFIRM_EMPTY)

    def test_confirm_none(self):
        self.assertEqual(validate_confirm("Пароль1!", None), MSG_CONFIRM_EMPTY)

    def test_confirm_mismatch(self):
        self.assertEqual(validate_confirm("Пароль1!", "Пароль2!"), MSG_CONFIRM_MISMATCH)


class TestValidateRegistration(unittest.TestCase):

    def test_full_success(self):
        result, msg = validate_registration("john_doe", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(msg, MSG_OK)

    def test_full_success_phone(self):
        result, msg = validate_registration("+7-999-123-4567", "Пароль1!", "Пароль1!")
        self.assertTrue(result)

    def test_full_success_email(self):
        result, msg = validate_registration("user@example.com", "Пароль1!", "Пароль1!")
        self.assertTrue(result)

    def test_fail_on_login(self):
        result, msg = validate_registration("admin", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(msg, MSG_LOGIN_BLACKLISTED)

    def test_fail_on_password(self):
        result, msg = validate_registration("john_doe", "коротк", "коротк")
        self.assertFalse(result)
        self.assertEqual(msg, MSG_PWD_TOO_SHORT)

    def test_fail_on_confirm(self):
        result, msg = validate_registration("john_doe", "Пароль1!", "Пароль2!")
        self.assertFalse(result)
        self.assertEqual(msg, MSG_CONFIRM_MISMATCH)

    def test_no_crash_on_none_inputs(self):
        result, msg = validate_registration(None, None, None)
        self.assertFalse(result)
        self.assertIsInstance(msg, str)


class TestMaskPassword(unittest.TestCase):

    def test_same_passwords_same_mask(self):
        self.assertEqual(mask_password("Пароль1!"), mask_password("Пароль1!"))

    def test_different_passwords_different_mask(self):
        self.assertNotEqual(mask_password("Пароль1!"), mask_password("Пароль2!"))

    def test_mask_hides_password(self):
        self.assertNotIn("Пароль1!", mask_password("Пароль1!"))


if __name__ == "__main__":
    unittest.main()
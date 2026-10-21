import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controller import RegistrationController
from src.db_repository import RegistrationRepository
from src.notifier import EmailNotifier
from src.user_interface import AbstractUserInterface
from src.validator import RegistrationValidator

class TestIntegrationControllerFullFlow(unittest.TestCase):


    def setUp(self):
        self.ui = Mock(spec=AbstractUserInterface)
        self.db = RegistrationRepository(":memory:")
        self.notifier = Mock()
        self.controller = RegistrationController(self.ui, self.db, self.notifier)

    def tearDown(self):
        self.db.close()

    def test_full_flow_success_saves_to_db_and_notifies(self):
        self.ui.get_input.side_effect = ["john_doe", "Пароль1!", "Пароль1!"]

        result, message = self.controller.process_registration()

        self.assertTrue(result)
        self.assertEqual(message, "")

        self.assertEqual(self.db.count(), 1)
        cached = self.db.get("john_doe", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(cached)
        self.assertTrue(cached["result"])

        # Проверка вызова заглушки внешней зависимости
        self.notifier.send.assert_called_once()
        sent_text = self.notifier.send.call_args[0][0]
        self.assertIn("john_doe", sent_text)
        self.assertIn("result=True", sent_text)

    def test_full_flow_invalid_data_not_saved_but_notified(self):
        self.ui.get_input.side_effect = ["admin", "Пароль1!", "Пароль1!"]

        result, message = self.controller.process_registration()

        self.assertFalse(result)
        self.assertIn("чёрный список", message)

        cached = self.db.get("admin", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(cached)
        self.assertFalse(cached["result"])

        self.notifier.send.assert_called_once()

    def test_second_call_uses_cache_not_validator(self):
        validator = Mock(spec=RegistrationValidator)
        validator.validate.return_value = (True, "")
        controller = RegistrationController(self.ui, self.db, self.notifier, validator=validator)

        self.ui.get_input.side_effect = [
            "john_doe", "Пароль1!", "Пароль1!",
            "john_doe", "Пароль1!", "Пароль1!",
        ]

        result1, _ = controller.process_registration()
        self.assertTrue(result1)
        self.assertEqual(validator.validate.call_count, 1)

        result2, _ = controller.process_registration()
        self.assertTrue(result2)
        self.assertEqual(validator.validate.call_count, 1)  # не изменился

        self.assertEqual(self.notifier.send.call_count, 2)
        # в первом сообщении источник "computed", во втором "cache"
        self.assertIn("computed", self.notifier.send.call_args_list[0][0][0])
        self.assertIn("cache", self.notifier.send.call_args_list[1][0][0])

class TestIntegrationWithRealEmailNotifier(unittest.TestCase):

    def test_real_email_notifier_receives_message(self):
        ui = Mock(spec=AbstractUserInterface)
        ui.get_input.side_effect = ["john_doe", "Пароль1!", "Пароль1!"]

        db = RegistrationRepository(":memory:")
        notifier = EmailNotifier()
        controller = RegistrationController(ui, db, notifier)

        result, _ = controller.process_registration()

        self.assertTrue(result)
        self.assertEqual(len(notifier.sent), 1)
        self.assertIn("john_doe", notifier.sent[0])

        db.close()


class TestIntegrationDatabasePersistence(unittest.TestCase):

    def test_record_survives_reopening_db(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            ui1 = Mock(spec=AbstractUserInterface)
            ui1.get_input.side_effect = ["john_doe", "Пароль1!", "Пароль1!"]
            db1 = RegistrationRepository(db_path)
            notifier1 = Mock()
            c1 = RegistrationController(ui1, db1, notifier1)
            c1.process_registration()
            db1.close()

            ui2 = Mock(spec=AbstractUserInterface)
            ui2.get_input.side_effect = ["john_doe", "Пароль1!", "Пароль1!"]
            db2 = RegistrationRepository(db_path)
            notifier2 = Mock()
            validator2 = Mock(spec=RegistrationValidator)
            c2 = RegistrationController(ui2, db2, notifier2, validator=validator2)

            result, _ = c2.process_registration()

            self.assertTrue(result)
            validator2.validate.assert_not_called()
            db2.close()
        finally:
            os.unlink(db_path)

class TestRepositoryUnit(unittest.TestCase):
    def setUp(self):
        self.db = RegistrationRepository(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_get(self):
        self.db.add("john_doe", "Пароль1!", "Пароль1!", True, "")
        cached = self.db.get("john_doe", "Пароль1!", "Пароль1!")
        self.assertEqual(cached, {"result": True, "message": ""})

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.db.get("no_such", "no_such", "no_such"))

    def test_delete_removes_record(self):
        self.db.add("john_doe", "Пароль1!", "Пароль1!", True, "")
        removed = self.db.delete("john_doe", "Пароль1!", "Пароль1!")
        self.assertEqual(removed, 1)
        self.assertIsNone(self.db.get("john_doe", "Пароль1!", "Пароль1!"))

    def test_add_replaces_existing(self):
        self.db.add("john_doe", "Пароль1!", "Пароль1!", True, "")
        self.db.add("john_doe", "Пароль1!", "Пароль1!", False, "новая ошибка")
        cached = self.db.get("john_doe", "Пароль1!", "Пароль1!")
        self.assertFalse(cached["result"])
        self.assertEqual(cached["message"], "новая ошибка")


class TestEmailNotifierUnit(unittest.TestCase):

    def test_send_appends_message(self):
        notifier = EmailNotifier()
        notifier.send("hello")
        self.assertEqual(notifier.sent, ["hello"])

    def test_send_multiple_messages(self):
        notifier = EmailNotifier()
        notifier.send("a")
        notifier.send("b")
        self.assertEqual(len(notifier.sent), 2)


if __name__ == "__main__":
    unittest.main()
import sqlite3


class RegistrationRepository:
    def __init__(self, db_path: str = ":memory:"):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                login    TEXT NOT NULL,
                password TEXT NOT NULL,
                confirm  TEXT NOT NULL,
                result   INTEGER NOT NULL,
                message  TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (login, password, confirm)
            )
        """)
        self._conn.commit()

    def add(self, login: str, password: str, confirm: str,
            result: bool, message: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO registrations "
            "(login, password, confirm, result, message) VALUES (?, ?, ?, ?, ?)",
            (login, password, confirm, int(result), message or ""),
        )
        self._conn.commit()

    def get(self, login: str, password: str, confirm: str):

        cur = self._conn.execute(
            "SELECT result, message FROM registrations "
            "WHERE login = ? AND password = ? AND confirm = ?",
            (login, password, confirm),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {"result": bool(row["result"]), "message": row["message"]}

    def delete(self, login: str, password: str, confirm: str) -> int:
        cur = self._conn.execute(
            "DELETE FROM registrations "
            "WHERE login = ? AND password = ? AND confirm = ?",
            (login, password, confirm),
        )
        self._conn.commit()
        return cur.rowcount

    def count(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) AS c FROM registrations")
        return cur.fetchone()["c"]

    def close(self) -> None:
        self._conn.close()

    def get_successful_users(self) -> list:
        cur = self._conn.execute(
            "SELECT login FROM registrations WHERE result = 1"
        )
        return [row["login"] for row in cur.fetchall()]
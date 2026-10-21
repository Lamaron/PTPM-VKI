from abc import ABC, abstractmethod


class AbstractNotifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


class EmailNotifier(AbstractNotifier):
    def __init__(self):
        self.sent: list[str] = []

    def send(self, message: str) -> None:
        self.sent.append(message)
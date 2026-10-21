from abc import ABC, abstractmethod


class AbstractUserInterface(ABC):

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        ...


class ConsoleUserInterface(AbstractUserInterface):
    def get_input(self, prompt: str) -> str:
        return input(prompt)
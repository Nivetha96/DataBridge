from abc import ABC, abstractmethod

class BaseConnector(ABC):

    @abstractmethod
    def list_files(self) -> list[str]:
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write_file(self, path: str, data: bytes) -> None:
        pass

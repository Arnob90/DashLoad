import pathlib
import abc
from typing import Callable


class IFileDeleter(abc.ABC):
    @abc.abstractmethod
    def delete_file(self, filepath: pathlib.Path, missing_ok: bool) -> None:
        pass


class FileDeleter(IFileDeleter):
    def delete_file(self, filepath: pathlib.Path, missing_ok: bool = False) -> None:
        filepath.unlink(missing_ok=missing_ok)


class MockFileDeleter(IFileDeleter):
    def __init__(self, delete_notify_callable: Callable[[pathlib.Path], None]) -> None:
        self.delete_notify_callable = delete_notify_callable

    def delete_file(self, filepath: pathlib.Path, missing_ok: bool = False) -> None:
        print("Attempted to delete", str(filepath))
        print("Set missing ok:", missing_ok)
        self.delete_notify_callable(filepath)

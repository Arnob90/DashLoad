import abc
import logging
import pathlib
import pypdl
from enum import Enum

from pypdl import utils
import extras


main_logger = logging.getLogger(__name__)


class IDownloader(abc.ABC):
    @abc.abstractmethod
    def resume_download(self, id: str) -> None:
        pass

    @abc.abstractmethod
    def pause_download(self, id: str) -> None:
        pass

    @abc.abstractmethod
    def cancel_download(self, id: str) -> None:
        pass

    @abc.abstractmethod
    def failed(self) -> bool:
        pass

    @abc.abstractmethod
    def succeeded(self) -> bool:
        pass

    @abc.abstractmethod
    def size(self) -> int | None:
        pass

    @abc.abstractmethod
    def finished_size(self) -> int | None:
        pass

    @abc.abstractmethod
    async def get_filepath(self) -> pathlib.Path:
        pass

    @abc.abstractmethod
    def get_last_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_download_speed(self) -> int | None:
        pass

    @abc.abstractmethod
    def get_is_paused(self) -> bool:
        pass


class PypdlDownloader(IDownloader):
    def __init__(
        self,
        download_url: str,
        filepath: pathlib.Path,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        },
    ) -> None:
        self._downloader: pypdl.Pypdl = pypdl.Pypdl()
        if not extras.is_valid_download_url(download_url):
            raise extras.InvalidDownloadUrlError()
        self._url: str = download_url
        self._cached_full_filepath: pathlib.Path | None = None
        self.filepath = filepath
        self.headers = headers
        self._downloader.start(
            download_url, block=False, file_path=str(filepath), headers=headers
        )
        self.paused = False

    def get_is_paused(self) -> bool:
        return self.paused

    def resume_download(self, id: str) -> None:
        if not self.paused:
            main_logger.info("Download is not paused")
            return
        self._downloader.start()
        self.paused = False

    def pause_download(self, id: str) -> None:
        if self.paused:
            main_logger.info("Download is already paused")
            return
        self._downloader.stop()
        self.paused = True

    def succeeded(self) -> bool:
        return self._downloader.completed

    def failed(self) -> bool:
        return len(self._downloader.failed) >= 1

    def size(self) -> int | None:
        return self._downloader.size

    def finished_size(self) -> int | None:
        return self._downloader.current_size

    async def get_filepath(self) -> pathlib.Path:
        if self._cached_full_filepath is not None:
            return pathlib.Path(self._cached_full_filepath)
        full_filepath_str: str = await utils.get_filepath(
            self._url, self.headers, str(self.filepath)
        )
        self._cached_full_filepath = pathlib.Path(full_filepath_str)
        return pathlib.Path(self._cached_full_filepath)

    def get_last_url(self) -> str:
        return self._url

    def get_download_speed(self) -> int | None:
        return self._downloader.speed


class DownloadStates(Enum):
    PAUSED = "paused"
    RESUMED = "resumed"
    CANCELLED = "cancelled"
    DOWNLOADING = "downloading"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# TODO: Finish the mock downloader
# class MockDownloader(IDownloader):
#     def __init__(self) -> None:
#         self._current_state = DownloadStates.DOWNLOADING
#
#     def resume_download(self, id: str) -> None:
#         self._current_state = DownloadStates.RESUMED
#
#     def pause_download(self, id: str) -> None:
#         self._current_state = DownloadStates.PAUSED
#
#     def cancel_download(self, id: str) -> None:
#         self._current_state = DownloadStates.CANCELLED
#
#     def failed(self) -> bool:
#         return self._current_state == DownloadStates.FAILED
#
#     def succeeded(self) -> bool:
#         return self._current_state == DownloadStates.SUCCEEDED
#
#     def size(self) -> int | None:
#         return 100
#
#     def finished_size(self) -> int | None:
#         return 50

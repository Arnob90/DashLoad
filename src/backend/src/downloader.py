import abc
import logging
import pathlib
from typing import Callable
import pypdl
from enum import Enum
from hook import Hook
from pypdl import utils
from download_cleanup import cleanup_download
import extras


main_logger = logging.getLogger(__name__)


class IDownloader(abc.ABC):
    @abc.abstractmethod
    def resume_download(self) -> None:
        pass

    @abc.abstractmethod
    def pause_download(self) -> None:
        pass

    @abc.abstractmethod
    def _start(self):
        """Starts downloading. SHOULD ONLY BE CALLED FROM DOWNLOAD MANAGER.
        DO NOT CALL FROM OUTSIDE"""

    @abc.abstractmethod
    async def cancel_download(self) -> None:
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

    @abc.abstractmethod
    def is_cancelled(self) -> bool:
        pass

    @abc.abstractmethod
    def connect_delete_request_notify_callable(
        self, notify_callable: Callable[[], None]
    ) -> None:
        pass

    @abc.abstractmethod
    async def delete_download_task(self, delete_on_disk: bool = False) -> None:
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
        self.download_start_args = (download_url,)
        self.download_start_kwargs = {
            "block": False,
            "file_path": str(filepath),
            "headers": headers,
        }
        self.paused = False
        self.cancelled = False
        self.delete_request_notify_callable = Hook()

    def connect_delete_request_notify_callable(
        self, notify_callable: Callable[[], None]
    ) -> None:
        self.delete_request_notify_callable.connect_with(notify_callable)

    def get_is_paused(self) -> bool:
        return self.paused

    def resume_download(self) -> None:
        if not self.paused or self.cancelled:
            main_logger.info("Download is not paused, or cancelled entirely")
            return
        self._start()
        self.paused = False

    def pause_download(self) -> None:
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
        if self.cancelled:
            return 0
        return self._downloader.current_size

    def finished(self) -> bool:
        return self.succeeded() or self.failed() or self.is_cancelled()

    def is_cancelled(self) -> bool:
        return self.cancelled

    async def get_filepath(self) -> pathlib.Path:
        gotten_filepath = await utils.get_filepath(
            self._url, self.headers, str(self.filepath)
        )
        gotten_filepath_converted = pathlib.Path(gotten_filepath)
        print(f"Got filepath: {gotten_filepath_converted}")
        return gotten_filepath_converted

    def get_last_url(self) -> str:
        return self._url

    def get_download_speed(self) -> int | None:
        return self._downloader.speed

    async def cancel_download(self) -> None:
        self._downloader.stop()
        recieved_filepath = await self.get_filepath()
        cleanup_download(recieved_filepath)
        self.cancelled = True

    def _start(self):
        self._downloader.start(*self.download_start_args,
                               **self.download_start_kwargs)

    async def delete_download_task(self, delete_on_disk: bool = False) -> None:
        if not self.finished():
            # If we are not done, we make sure to clean up, since we don't manage it anymore
            # After all, resource aquisition is initialization
            await self.cancel_download()
        if self.finished and delete_on_disk:
            recieved_filepath = await self.get_filepath()
            print("Recieved filepath: ", recieved_filepath)
            cleanup_download(recieved_filepath)
        self.delete_request_notify_callable()


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

from os import path
import pathlib
import downloader
import threading
from typing import Coroutine, List, Optional
from typing import Any
from uuid import uuid4
import debugpy
from downloader import PypdlDownloader
import extras
import internet_connections
import downloaditem
import asyncio
import downloadstates
from extras import (
    DownloadIdMissingError,
    DownloadToAnExistingPathError,
    InvalidDownloadUrlError,
)
import logging
from pydantic import BaseModel
import download_cleanup

main_logger = logging.getLogger(__name__)


def _get_queue_download_from_item(
    given_item: downloaditem.DownloadItem,
) -> downloadstates.QueuedDownloadInfo:
    return downloadstates.QueuedDownloadInfo(
        download_id=given_item.download_id,
        filepath=str(given_item.download_task.get_short_filepath()),
        last_url=given_item.download_task.get_last_url(),
        filename=None,
        filesize=None,
    )


class SerializedDownloadItems(BaseModel):
    download_items: dict[str, downloadstates.DownloadInfoState]


class DownloadManager:
    def __init__(self):
        self.download_items: dict[str, downloaditem.DownloadItem] = {}
        self.terminal_download_items: dict[
            str,
            downloadstates.FailedDownloadInfo
            | downloadstates.CancelledDownloadInfo
            | downloadstates.PausedDownloadInfo
            | downloadstates.QueuedDownloadInfo,
        ] = {}
        self.network_tracker = internet_connections.NetworkConnectionPoller()

    async def queue_download(self, queue_info: downloadstates.QueuedDownloadInfo):
        if not extras.check_if_url_syntax_valid(queue_info.last_url):
            raise InvalidDownloadUrlError()

        if self.network_tracker.available:
            return await self.add_download_item(
                downloaditem.DownloadItem(
                    PypdlDownloader(
                        download_url=queue_info.last_url,
                        filepath=pathlib.Path(queue_info.filepath),
                    ),
                    download_id=queue_info.download_id,
                )
            )
        if queue_info.download_id is None:
            raise DownloadIdMissingError("The info to queue doesn't even have an id!!!")
        self.terminal_download_items[queue_info.download_id] = queue_info
        # Use a list to store a pointer on the heap
        # That way, when it is copied into the closure, the pointer is copied
        # Not the value
        done_running = [False]

        def handle_internet_access():
            if done_running[0]:
                return
            if not self.network_tracker.available:
                return

            async def async_wrapper():
                if queue_info.download_id is None:
                    raise DownloadIdMissingError(
                        "The info to queue doesn't even have an id!!!"
                    )
                try:
                    # Should be impossible with disciplined coding, assuming the item is not mutated
                    # But you can never be too sure :)
                    await self.add_download_item(
                        downloaditem.DownloadItem(
                            PypdlDownloader(
                                download_url=queue_info.last_url,
                                filepath=pathlib.Path(queue_info.filepath),
                            ),
                            download_id=queue_info.download_id,
                        ),
                    )
                except Exception as err:
                    main_logger.info(err)

                finally:
                    del self.terminal_download_items[queue_info.download_id]
                    done_running[0] = True

            def runner():
                asyncio.run(async_wrapper())

            threading.Thread(target=runner, daemon=True).start()

        self.network_tracker.connection_status_changed_hook.connect_with(
            handle_internet_access
        )
        return queue_info.download_id

    async def add_download_item(self, download_item: downloaditem.DownloadItem) -> str:
        # TODO: Remove this debugging statement
        # debugpy.listen(("localhost", 5678))
        # print("debugpy listening on 5678", flush=True)
        # debugpy.wait_for_client()
        # debugpy.breakpoint()
        id_to_filepaths = await self.get_id_to_filepaths()
        filepath_to_download_to = await download_item.download_task.get_filepath()
        for id, filepath in id_to_filepaths:
            if filepath == filepath_to_download_to:
                raise DownloadToAnExistingPathError(
                    f"File with this name is already being downloaded. Download id:{id}"
                )
        if filepath_to_download_to.exists():
            raise DownloadToAnExistingPathError(
                f"A file already exists on disk at path {filepath_to_download_to}"
            )
        self.download_items[download_item.download_id] = download_item
        download_item.download_task._start()

        def on_delete():
            main_logger.info("Deleting download info")
            del self.download_items[download_item.download_id]

        def on_retry():
            main_logger.info("Retrying download")
            self.download_items[download_item.download_id] = download_item
            del self.terminal_download_items[download_item.download_id]

        download_item.download_task.connect_delete_request_notify_callable(on_delete)
        download_item.download_task.connect_retry_request_notify_callable(on_retry)

        return download_item.download_id

    async def resume_download(self, download_id: str):
        if download_id in self.download_items:
            self.download_items[download_id].download_task.resume_download()
            return
        if download_id in self.terminal_download_items:
            terminal_download = await self.get_download_info_by_id(download_id)
            await self.add_download_item(
                downloaditem.DownloadItem(
                    PypdlDownloader(
                        download_url=terminal_download.last_url,
                        filepath=pathlib.Path(terminal_download.filepath),
                    ),
                    download_id=terminal_download.download_id,
                ),
            )
            del self.terminal_download_items[download_id]
            return
        else:
            raise ValueError("The download id doesn't exist in manager")

    def pause_download(self, download_id: str):
        if download_id in self.download_items:
            self.download_items[download_id].download_task.pause_download()
            return

        # if it's terminal, then it's not running at all!
        if download_id in self.terminal_download_items:
            main_logger.info("Download is already stopped")
            return

        raise ValueError("The download id doesn't exist in manager")

    async def cancel_download(self, download_id: str):
        if download_id in self.download_items:
            await self.download_items[download_id].download_task.cancel_download()
            # Get function will lazily populate terminal. No need to be so eager!
            return

        if download_id in self.terminal_download_items:
            terminal_download = await self.get_download_info_by_id(download_id)
            download_filepath = pathlib.Path(terminal_download.filepath)
            download_cleanup.cleanup_download(download_filepath)
            resulting_state = downloadstates.CancelledDownloadInfo(
                download_id=download_id,
                filepath=str(download_filepath),
                filename=download_filepath.name,
                filesize=terminal_download.filesize,
                last_url=terminal_download.last_url,
            )
            self.terminal_download_items[download_id] = resulting_state
            return

        raise ValueError("The download id doesn't exist in manager")

    async def delete_download_task(self, download_id: str, delete_file: bool):
        if delete_file:
            await self.cancel_download(download_id)
        else:
            self.pause_download(download_id)
        if download_id in self.download_items:
            self.download_items.pop(download_id)
            return
        self.terminal_download_items.pop(download_id)

    async def retry_download(self, download_id: str):
        if download_id in self.download_items:
            self.download_items[download_id].download_task.retry_download()
            return
        elif download_id in self.terminal_download_items:
            terminal_download = await self.get_download_info_by_id(download_id)
            await self.add_download_item(
                downloaditem.DownloadItem(
                    PypdlDownloader(
                        download_url=terminal_download.last_url,
                        filepath=pathlib.Path(terminal_download.filepath),
                    ),
                    download_id=terminal_download.download_id,
                ),
            )
            return
        raise ValueError("The download id doesn't exist in manager")

    async def get_id_to_filepaths(self) -> List[tuple[str, pathlib.Path]]:
        ids: List[str] = []
        filepath_get_tasks: List[Coroutine[Any, Any, pathlib.Path]] = []
        for id, download_task in self.download_items.items():
            filepath_get_task = download_task.download_task.get_filepath()
            filepath_get_tasks.append(filepath_get_task)
            ids.append(id)
        filepaths = await asyncio.gather(*filepath_get_tasks)
        return list(zip(ids, filepaths))

    async def get_download_info_by_id(
        self, download_id: str
    ) -> downloadstates.DownloadInfoState:
        if download_id in self.terminal_download_items:
            return self.terminal_download_items[download_id]
        state = await self.download_items[download_id].get_download_state()
        if (
            isinstance(state, downloadstates.FailedDownloadInfo)
            or isinstance(state, downloadstates.CancelledDownloadInfo)
            or isinstance(state, downloadstates.PausedDownloadInfo)
        ):
            # Lazily populate the terminal download states
            self.terminal_download_items[download_id] = state
            self.download_items.pop(download_id)

        if (
            isinstance(state, downloadstates.DownloadingInfo)
            and not self.network_tracker.available
        ):
            return downloadstates.PendingDownloadInfo(
                download_id=state.download_id,
                filename=state.filename,
                filepath=state.filepath,
                filesize=state.filesize,
                last_url=state.last_url,
            )
        return state

    async def get_all_download_infos(self) -> list[downloadstates.DownloadInfoState]:
        download_state_futures: list[
            Coroutine[Any, Any, downloadstates.DownloadInfoState]
        ] = []
        download_item_ids = list(self.download_items.keys())
        terminal_items_ids = list(self.terminal_download_items.keys())
        all_ids = list(download_item_ids) + list(terminal_items_ids)
        for download_id in all_ids:
            download_state_futures.append(self.get_download_info_by_id(download_id))
        return await asyncio.gather(*download_state_futures)

    async def get_all_id_to_download_infos(
        self,
    ) -> dict[str, downloadstates.DownloadInfoState]:
        download_state_futures: list[
            Coroutine[Any, Any, downloadstates.DownloadInfoState]
        ] = []
        required_infos: list[downloadstates.DownloadInfoState] = []
        all_ids = list(self.download_items.keys()) + list(
            self.terminal_download_items.keys()
        )
        for download_id in all_ids:
            download_state_futures.append(self.get_download_info_by_id(download_id))
        required_infos = await asyncio.gather(*download_state_futures)
        required_dict: dict[str, downloadstates.DownloadInfoState] = {}
        for info in required_infos:
            if info.download_id is None:
                raise DownloadIdMissingError("Download id is None")
            required_dict[info.download_id] = info
        return required_dict

    async def add_pypdl_download(
        self, url: str, filepath: pathlib.Path, id: str | None = None
    ) -> str:
        id_to_use: str = ""
        if id is None:
            id_to_use = uuid4().hex
        else:
            id_to_use = id

        if not self.network_tracker.available:
            ret_id = await self.queue_download(
                downloadstates.QueuedDownloadInfo(
                    download_id=id_to_use,
                    filepath=str(filepath),
                    filename=None,
                    filesize=None,
                    last_url=url,
                )
            )
            return ret_id
        ret_id = await self.add_download_item(
            downloaditem.DownloadItem(
                downloader.PypdlDownloader(url, filepath),
            ),
        )
        return ret_id

    async def shutdown(self):
        """
        Pause all downloads and prepares for shutdown. The download manager will not be usable after this, so do not use.
        DO NOT SERIALIZE AFTER SHUTDOWN. ALL STATES WILL BECOME PAUSED AND THUS STALE
        """
        for download_item in self.download_items.values():
            state_of_download = await download_item.get_download_state()
            if isinstance(state_of_download, downloadstates.DownloadingInfo):
                download_item.download_task.pause_download()

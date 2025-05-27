from argparse import ArgumentError
from os import path
import pathlib
from typing import Coroutine, List
from typing import Any
from downloader import PypdlDownloader
import downloaditem
import asyncio
import downloadstates
from extras import (
    DownloadIdMissingError,
    DownloadToAnExistingPathError,
    ISecretHolder,
    SecretHolder,
)
import logging
from pydantic import BaseModel
import extras

main_logger = logging.getLogger(__name__)


class SerializedDownloadItems(BaseModel):
    download_items: dict[str, downloadstates.DownloadInfoState]


class DownloadManager:
    def __init__(self):
        self.download_items: dict[str, downloaditem.DownloadItem] = {}
        self.failed_or_cancelled_download_items: dict[
            str,
            downloadstates.FailedDownloadInfo | downloadstates.CancelledDownloadInfo,
        ] = {}

    async def add_download_item(self, download_item: downloaditem.DownloadItem) -> str:
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

        download_item.download_task.connect_delete_request_notify_callable(on_delete)

        return download_item.download_id

    def get_download_item(self, download_id: str) -> downloaditem.DownloadItem:
        return self.download_items[download_id]

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
        if download_id in self.failed_or_cancelled_download_items:
            return self.failed_or_cancelled_download_items[download_id]
        state = await self.download_items[download_id].get_download_state()
        if isinstance(state, downloadstates.FailedDownloadInfo) or isinstance(
            state, downloadstates.CancelledDownloadInfo
        ):
            # Lazily populate the terminal download states
            self.failed_or_cancelled_download_items[download_id] = state
            self.download_items.pop(download_id)
        return state

    async def get_all_download_infos(self) -> list[downloadstates.DownloadInfoState]:
        download_state_futures: list[
            Coroutine[Any, Any, downloadstates.DownloadInfoState]
        ] = []
        for download_id in self.download_items:
            download_state_futures.append(self.get_download_info_by_id(download_id))
        return await asyncio.gather(*download_state_futures)

    async def get_all_id_to_download_infos(
        self,
    ) -> dict[str, downloadstates.DownloadInfoState]:
        download_state_futures: list[
            Coroutine[Any, Any, downloadstates.DownloadInfoState]
        ] = []
        required_infos: list[downloadstates.DownloadInfoState] = []
        for download_id in self.download_items:
            download_state_futures.append(self.get_download_info_by_id(download_id))
        required_infos = await asyncio.gather(*download_state_futures)
        required_dict: dict[str, downloadstates.DownloadInfoState] = {}
        for info in required_infos:
            if info.download_id is None:
                raise DownloadIdMissingError("Download id is None")
            required_dict[info.download_id] = info
        return required_dict

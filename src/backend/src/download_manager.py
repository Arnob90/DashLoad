from os import path
import pathlib
from typing import Coroutine, List
from typing import Any
import downloaditem
import asyncio
import downloadstates
from extras import DownloadToAnExistingPathError, ISecretHolder, SecretHolder
import logging

main_logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, secret: ISecretHolder):
        self.download_items: dict[str, downloaditem.DownloadItem] = {}

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
        return await self.download_items[download_id].get_download_state()

    async def get_all_download_infos(self) -> list[downloadstates.DownloadInfoState]:
        download_state_futures: list[
            Coroutine[Any, Any, downloadstates.DownloadInfoState]
        ] = []
        for download_item in self.download_items.values():
            download_state_futures.append(download_item.get_download_state())
        return await asyncio.gather(*download_state_futures)

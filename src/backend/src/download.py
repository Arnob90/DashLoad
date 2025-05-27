# This file is deprecated btw
import abc
import pypdl
from pypdl import utils
import uuid
from typing import Any, Awaitable, Callable
from pydantic import BaseModel
import pathlib
from dataclasses import dataclass
import extras
import asyncio
import functools
import json
import warnings

warnings.warn(
    "The download module is deprecated, and only exists as a prototype/reference",
    DeprecationWarning,
)


class SingleMutexClass(abc.ABC):
    @abc.abstractmethod
    def get_mutex(self) -> asyncio.Lock:
        pass


def use_mutex(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @functools.wraps(func)
    async def wrapper(self: SingleMutexClass, *args, **kwargs) -> Any:
        async with self.get_mutex():
            return await func(self, *args, **kwargs)

    return wrapper


@dataclass(frozen=True)
class PausedDownload:
    filesize_downloaded: int | None
    filesize: int | None


class DownloadInfoJsonObj(BaseModel):
    url: str
    etag: str
    segments: int


class DownloadInfoState(BaseModel, abc.ABC):
    download_id: str | None
    filename: str | None
    filepath: str
    filesize: int | None
    type: str
    last_url: str


class DownloadingInfo(DownloadInfoState):
    downloaded_file_portion: int | None
    type: str = "DownloadingInfo"
    download_speed: float | None


class PausedDownloadInfo(DownloadInfoState):
    downloaded_file_portion: int | None
    type: str = "PausedDownloadInfo"


class FailedDownloadInfo(DownloadInfoState):
    type: str = "FailedDownloadInfo"


class SucceededDownloadInfo(DownloadInfoState):
    type: str = "SucceededDownloadInfo"


class CancelledDownloadInfo(DownloadInfoState):
    type: str = "CancelledDownloadInfo"


@dataclass(frozen=True)
class ExtraInfos:
    download_id: str
    url: str
    filepath: str


class Downloader(SingleMutexClass):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
    }

    def __init__(self) -> None:
        self.id_to_downloaders: dict[str, pypdl.Pypdl | PausedDownload] = {}
        self.id_to_info: dict[str, ExtraInfos] = {}
        self.id_to_download_cancelled_infos: dict[str, CancelledDownloadInfo] = {}
        self.mutex = asyncio.Lock()

    def get_mutex(self):
        return self.mutex

    async def download(self, download_url: str, filepath: pathlib.Path):
        if not extras.is_valid_download_url(download_url):
            raise extras.InvalidDownloadUrlError()
        filepath_str: str = await utils.get_filepath(
            download_url, self.headers, str(filepath)
        )
        prev_id = await self.get_id_from_filepath(pathlib.Path(filepath_str))
        if prev_id is not None:
            required_info = self.id_to_info[prev_id]
            _ = self.resume_download(prev_id)
            return prev_id
        downloader = pypdl.Pypdl()
        downloader.start(download_url, block=False, file_path=str(filepath))
        id = uuid.uuid4().hex
        self.id_to_downloaders.update({id: downloader})
        required_info = ExtraInfos(
            download_id=id,
            url=download_url,
            filepath=filepath_str,
        )
        self.id_to_info.update({id: required_info})
        return id

    async def get_id_from_filepath(self, given_filepath: pathlib.Path) -> str | None:
        for id, info in self.id_to_info.items():
            if pathlib.Path(info.filepath) == given_filepath:
                return id
        return None

    async def create_download_info_from_download_obj(
        self, id: str
    ) -> DownloadInfoState:
        if id not in self.id_to_downloaders:
            raise ValueError("The given id is not being downloaded")
        download_obj = self.id_to_downloaders[id]
        download_info = self.id_to_info[id]
        required_filepath = download_info.filepath
        required_filename = pathlib.Path(required_filepath).name
        if isinstance(download_obj, PausedDownload):
            return PausedDownloadInfo(
                download_id=id,
                filename=str(required_filename),
                filepath=required_filepath,
                filesize=download_obj.filesize,
                downloaded_file_portion=download_obj.filesize_downloaded,
                last_url=download_info.url,
            )
        elif len(download_obj.failed) >= 1:
            return FailedDownloadInfo(
                download_id=id,
                filename=str(required_filename),
                filepath=required_filepath,
                filesize=download_obj.size,
                last_url=download_info.url,
            )
        elif len(download_obj.success) >= 1:
            return SucceededDownloadInfo(
                download_id=id,
                filename=str(required_filename),
                filepath=required_filepath,
                filesize=download_obj.size,
                last_url=download_info.url,
            )
        else:
            return DownloadingInfo(
                download_id=id,
                filename=str(required_filename),
                filepath=required_filepath,
                filesize=download_obj.size,
                downloaded_file_portion=download_obj.current_size,
                download_speed=download_obj.speed,
                last_url=download_info.url,
            )

    async def create_download_info_from_cancelled_download(self, id: str):
        cancelled_download_info = self.id_to_download_cancelled_infos.get(id)
        if cancelled_download_info is None:
            raise ValueError("The id to cancelled download doesn't exist")
        return cancelled_download_info

    async def query_downloads_info(self):
        final_result: list[DownloadInfoState] = []
        for id in self.id_to_downloaders:
            required_info = await self.create_download_info_from_download_obj(id)
            final_result.append(required_info)
        for id in self.id_to_download_cancelled_infos:
            final_result.append(
                await self.create_download_info_from_cancelled_download(id)
            )
        return final_result

    async def get_download_info_from_id(self, id: str):
        return self.create_download_info_from_download_obj(id)

    async def pause_download(self, id: str):
        if id not in self.id_to_downloaders:
            raise ValueError("The given id is not being downloaded")
        required_download: pypdl.Pypdl | PausedDownload = self.id_to_downloaders[id]
        if isinstance(required_download, PausedDownload):
            raise RuntimeError("A download can't be paused twice!")
        required_download.stop()
        download_state = PausedDownload(
            filesize_downloaded=required_download.current_size,
            filesize=required_download.size,
        )
        self.id_to_downloaders[id] = download_state

    async def get_download_info_json(
        self, filepath: pathlib.Path
    ) -> DownloadInfoJsonObj:
        json_obj = DownloadInfoJsonObj.model_validate_json(filepath.read_text())
        print(json_obj)
        return json_obj

    async def delete_download_task(self, id: str, delete_file_on_disk=False):
        print(delete_file_on_disk)
        if id not in self.id_to_downloaders:
            return None
        downloader = self.id_to_downloaders[id]
        if not isinstance(downloader, PausedDownload):
            downloader.stop()
        self.id_to_downloaders.pop(id)
        filepath_to_delete = self.id_to_info[id].filepath
        json_path = pathlib.Path(filepath_to_delete + ".json")
        print(json_path)
        info_json = await self.get_download_info_json(json_path)
        segments = info_json.segments
        print(segments)
        self.id_to_info.pop(id)
        if delete_file_on_disk:
            if segments == 1:
                to_delete_file = pathlib.Path(filepath_to_delete)
                to_delete_file.unlink()
                return
            for i in range(0, segments):
                to_delete_file = pathlib.Path(f"{filepath_to_delete}.{i}")
                print("Deleting segmented download")
                print(str(to_delete_file))
                to_delete_file.unlink()
            json_path.unlink()

    async def resume_download(self, id: str):
        if id not in self.id_to_downloaders:
            raise ValueError("The given id is not being downloaded")
        download_url = self.id_to_info[id].url
        # We take the full filepath, so even if the filename changes on server
        # It doesn't affect the resuming
        filepath_to_download_to = pathlib.Path(self.id_to_info[id].filepath)
        downloader = pypdl.Pypdl()
        downloader.start(
            download_url, block=False, file_path=str(filepath_to_download_to)
        )
        self.id_to_downloaders[id] = downloader

    async def cancel_download(self, id: str):
        required_info = await self.get_download_info_from_id(id)
        if not isinstance(required_info, DownloadingInfo):
            raise ValueError("The given id is not even being downloaded")
        cancelled_info = CancelledDownloadInfo(
            download_id=required_info.download_id,
            filename=required_info.filename,
            filesize=required_info.filesize,
            filepath=required_info.filepath,
            last_url=required_info.last_url,
        )
        await self.delete_download_task(id)
        self.id_to_download_cancelled_infos.update({id: cancelled_info})

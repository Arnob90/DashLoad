import pypdl
from pypdl import utils
import uuid
from pydantic import BaseModel
import pathlib
from dataclasses import dataclass


class DownloadInfo(BaseModel):
    download_id: str | None
    filesize: int | None
    downloaded_file_portion: int | None
    filename: str | None
    filepath: str


@dataclass(frozen=True)
class ExtraInfos:
    download_id: str
    url: str
    filepath: str


class Downloader:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
    }

    def __init__(self) -> None:
        self.download_tasks: dict[str, pypdl.Pypdl] = {}
        self.id_to_info: dict[str, ExtraInfos] = {}

    async def download(self, download_url: str, filepath: pathlib.Path):
        downloader = pypdl.Pypdl()
        downloader.start(download_url, block=False, file_path=str(filepath))
        id = uuid.uuid4().hex
        filepath_str: str = await utils.get_filepath(
            download_url, self.headers, str(filepath)
        )
        self.download_tasks.update({id: downloader})
        required_info = ExtraInfos(
            download_id=id, url=download_url, filepath=filepath_str
        )
        self.id_to_info.update({id: required_info})
        return id

    def create_download_info_from_download_obj(self, id: str):
        if id not in self.download_tasks:
            raise ValueError("The given id is not being downloaded")
        download_obj = self.download_tasks[id]
        required_filepath = self.id_to_info[id].filepath
        required_info = DownloadInfo(
            filename=str(pathlib.Path(required_filepath).name),
            download_id=id,
            filesize=download_obj.size,
            downloaded_file_portion=download_obj.current_size,
            filepath=required_filepath,
        )
        return required_info

    async def query_downloads_info(self):
        final_result: list[DownloadInfo] = []
        for id in self.download_tasks:
            required_info = self.create_download_info_from_download_obj(id)
            final_result.append(required_info)
        return final_result

    async def get_download_info_from_id(self, id: str):
        return self.create_download_info_from_download_obj(id)

    async def pause_download(self, id: str):
        if id not in self.download_tasks:
            raise ValueError("The given id is not being downloaded")
        required_download: pypdl.Pypdl = self.download_tasks[id]
        required_download.stop()

    async def delete_download_task(self, id: str, delete_file_on_disk=False):
        if id not in self.download_tasks:
            return None
        self.download_tasks[id].stop()
        self.download_tasks.pop(id)
        filepath_to_delete = self.id_to_info[id].filepath
        self.id_to_info.pop(id)
        if delete_file_on_disk:
            to_delete_file = pathlib.Path(filepath_to_delete)
            to_delete_file.unlink()

    async def resume_download(self, id: str):
        if id not in self.download_tasks:
            raise ValueError("The given id is not being downloaded")
        download_url = self.id_to_info[id].url
        # We take the full filepath, so even if the filename changes on server
        # It doesn't affect the resuming
        filepath_to_download_to = pathlib.Path(self.id_to_info[id].filepath)
        downloader = pypdl.Pypdl()
        downloader.start(
            download_url, block=False, file_path=str(filepath_to_download_to)
        )
        self.download_tasks[id] = downloader

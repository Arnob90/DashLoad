from aiohttp.helpers import strip_auth_from_url
import pypdl
from pypdl import utils
import uuid
from pydantic import BaseModel
import pathlib


def get_inverse_map[K, V](given_map: dict[K, V]) -> dict[V, K]:
    required_map: dict[V, K] = {}
    for key, val in given_map.items():
        if required_map.get(val) is None:
            raise ValueError("The given map is not bijective")
        required_map.update({val: key})
    return required_map


class DownloadInfo(BaseModel):
    download_id: str | None
    filesize: int | None
    downloaded_file_portion: int | None
    filename: str | None
    filepath: str


class Downloader:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "range": "bytes=-10485760",
    }

    def __init__(self) -> None:
        self.download_tasks: dict[str, pypdl.Pypdl] = {}
        self.id_to_filepaths: dict[str, str] = {}

    async def download(self, download_url: str, filepath: pathlib.Path):
        downloader = pypdl.Pypdl()
        downloader.start(download_url, block=False, file_path=str(filepath))
        id = uuid.uuid4().hex
        filepath_str: str = await utils.get_filepath(
            download_url, self.headers, str(filepath)
        )
        self.download_tasks.update({id: downloader})
        self.id_to_filepaths.update({id: filepath_str})
        return id

    def create_download_info_from_download_obj(self, id: str):
        download_obj = self.download_tasks[id]
        required_info = DownloadInfo(
            filename=str(pathlib.Path(self.id_to_filepaths[id]).name),
            download_id=id,
            filesize=download_obj.size,
            downloaded_file_portion=download_obj.current_size,
            filepath=self.id_to_filepaths[id],
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

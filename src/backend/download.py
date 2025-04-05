from typing import Iterable
import pypdl
import dataclasses
import uuid
from pydantic import BaseModel


class DownloadInfo(BaseModel):
    download_id: str | None
    filesize: int | None
    downloaded_file_portion: int | None


class Downloader:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "range": "bytes=-10485760",
    }

    def __init__(self) -> None:
        self.download_tasks: dict[str, pypdl.Pypdl] = {}

    def download(self, download_url: str, filepath: str):
        downloader = pypdl.Pypdl()
        downloader.start(download_url, block=False)
        id = uuid.uuid4().hex
        self.download_tasks.update({uuid.uuid4().hex: downloader})
        return id

    def query_downloads_info(self) -> Iterable[DownloadInfo]:
        for id, task in self.download_tasks.items():
            yield DownloadInfo(
                download_id=id,
                filesize=task.size,
                downloaded_file_portion=task.current_size,
            )

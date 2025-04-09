import pypdl
from pypdl import utils
import uuid
from pydantic import BaseModel
import pathlib


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

    async def query_downloads_info(self):
        final_result: list[DownloadInfo] = []
        for id, task in self.download_tasks.items():
            filepath = self.id_to_filepaths[id]
            filename = pathlib.Path(filepath).name
            required_info = DownloadInfo(
                filename=filename,
                download_id=id,
                filesize=task.size,
                downloaded_file_portion=task.current_size,
                filepath=filepath,
            )
            final_result.append(required_info)
        return final_result

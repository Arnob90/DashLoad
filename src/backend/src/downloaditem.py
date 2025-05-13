import pypdl
import pathlib
from deleter import FileDeleter, IFileDeleter
import downloadstates
import uuid
import downloader
from pydantic import BaseModel
from downloadinfojson import DownloadInfoJsonObj
from downloadmetainfojson import (
    DownloadInfoJsonGetter,
    IDownloadInfoJsonGetter,
    DownloadMetadataMissingError,
)
import extras


def get_download_info_json_path(download_path: pathlib.Path):
    json_path = extras.add_extension_to_path(download_path, ".json")
    return json_path


def cleanup_download(
    download_path: pathlib.Path,
    file_deleter: IFileDeleter = FileDeleter(),
    json_getter: IDownloadInfoJsonGetter = DownloadInfoJsonGetter(),
):
    try:
        json_obj = json_getter.get_json(download_path)
        segments = json_obj.segments
        if segments == 1:
            file_deleter.delete_file(download_path, missing_ok=True)
            return
        for i in range(0, segments):
            to_delete_file = pathlib.Path(f"{download_path}.{i}")
            file_deleter.delete_file(to_delete_file, missing_ok=True)
        json_path = get_download_info_json_path(download_path)
        file_deleter.delete_file(json_path, missing_ok=True)
    except DownloadMetadataMissingError as e:
        print(e)


class DownloadItem:
    def __init__(self, download_task: downloader.IDownloader) -> None:
        self.download_id = uuid.uuid4().hex
        self.download_task = download_task

    async def get_download_state(self) -> downloadstates.DownloadInfoState:
        self.filepath = await self.download_task.get_filepath()
        filename = pathlib.Path(self.filepath).name
        if self.download_task.get_is_paused():
            return downloadstates.PausedDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(self.filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
                downloaded_file_portion=self.download_task.finished_size(),
            )
        if self.download_task.succeeded():
            return downloadstates.SucceededDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(self.filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
            )
        elif self.download_task.failed():
            return downloadstates.FailedDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(self.filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
            )
        else:
            return downloadstates.DownloadingInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(self.filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
                downloaded_file_portion=self.download_task.finished_size(),
                download_speed=self.download_task.get_download_speed(),
            )

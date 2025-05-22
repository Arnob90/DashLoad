import pathlib
import downloadstates
import uuid
import downloader


class DownloadItem:
    def __init__(self, download_task: downloader.IDownloader) -> None:
        self.download_id = uuid.uuid4().hex
        self.download_task = download_task

    async def get_download_state(self) -> downloadstates.DownloadInfoState:
        filepath = await self.download_task.get_filepath()
        filename = pathlib.Path(filepath).name
        if self.download_task.get_is_paused():
            return downloadstates.PausedDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
                downloaded_file_portion=self.download_task.finished_size(),
            )
        if self.download_task.succeeded():
            return downloadstates.SucceededDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
            )
        elif self.download_task.failed():
            return downloadstates.FailedDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
            )
        elif self.download_task.is_cancelled():
            return downloadstates.CancelledDownloadInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
            )
        else:
            return downloadstates.DownloadingInfo(
                download_id=self.download_id,
                filename=str(filename),
                filepath=str(filepath),
                filesize=self.download_task.size(),
                last_url=self.download_task.get_last_url(),
                downloaded_file_portion=self.download_task.finished_size(),
                download_speed=self.download_task.get_download_speed(),
            )

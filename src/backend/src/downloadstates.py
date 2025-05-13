from dataclasses import dataclass
from pydantic import BaseModel
import abc


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

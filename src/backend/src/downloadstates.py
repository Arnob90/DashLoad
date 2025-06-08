from dataclasses import dataclass
import typing
from pydantic import BaseModel, Discriminator, Field, TypeAdapter
import abc
from typing import Annotated, Literal, Union


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
    last_url: str


class DownloadingInfo(DownloadInfoState):
    downloaded_file_portion: int | None
    type: Literal["DownloadingInfo"] = "DownloadingInfo"
    download_speed: float | None


class PausedDownloadInfo(DownloadInfoState):
    downloaded_file_portion: int | None
    type: Literal["PausedDownloadInfo"] = "PausedDownloadInfo"


class FailedDownloadInfo(DownloadInfoState):
    type: Literal["FailedDownloadInfo"] = "FailedDownloadInfo"


class SucceededDownloadInfo(DownloadInfoState):
    type: Literal["SucceededDownloadInfo"] = "SucceededDownloadInfo"


class CancelledDownloadInfo(DownloadInfoState):
    type: Literal["CancelledDownloadInfo"] = "CancelledDownloadInfo"


class PendingDownloadInfo(DownloadInfoState):
    type: Literal["PendingDownloadInfo"] = "PendingDownloadInfo"


class QueuedDownloadInfo(DownloadInfoState):
    type: Literal["QueuedDownloadInfo"] = "QueuedDownloadInfo"


DownloadStateVariants = Annotated[
    Union[
        DownloadingInfo,
        PausedDownloadInfo,
        FailedDownloadInfo,
        SucceededDownloadInfo,
        CancelledDownloadInfo,
        QueuedDownloadInfo,
        PendingDownloadInfo,
    ],
    Field(discriminator="type"),
]

variant_adapter = TypeAdapter(DownloadStateVariants)


def convert_base_type_to_variants(
    given_info: DownloadInfoState,
) -> DownloadStateVariants:
    return variant_adapter.validate_python(given_info)


def convert_variants_to_base_type(
    given_info: DownloadStateVariants,
) -> DownloadInfoState:
    return given_info

from deleter import IFileDeleter, FileDeleter
from downloadmetainfojson import (
    IDownloadInfoJsonGetter,
    DownloadMetadataMissingError,
    DownloadInfoJsonGetter,
)
import pathlib
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

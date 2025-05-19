import pathlib
import logging
from download_cleanup import cleanup_download
from deleter import MockFileDeleter
from downloadmetainfojson import MockDownloadInfoJsonGetter
from downloadinfojson import DownloadInfoJsonObj

# Set up logging for the test module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_cleanup_download_deletes_segments_and_json():
    deleted_files = []

    def notify(path: pathlib.Path):
        logger.info(f"Mock delete: {path}")
        deleted_files.append(path)

    mock_deleter = MockFileDeleter(delete_notify_callable=notify)
    json_obj = DownloadInfoJsonObj(
        segments=3, url="http://fake.url", etag="fake_etag")
    mock_json_getter = MockDownloadInfoJsonGetter(given_json=json_obj)

    download_path = pathlib.Path("/fake/download/file")

    logger.info(f"Starting cleanup for {download_path}")
    cleanup_download(
        download_path=download_path,
        file_deleter=mock_deleter,
        json_getter=mock_json_getter,
    )

    expected = [
        pathlib.Path("/fake/download/file.0"),
        pathlib.Path("/fake/download/file.1"),
        pathlib.Path("/fake/download/file.2"),
        pathlib.Path("/fake/download/file.json"),
    ]

    logger.info("Deleted files: %s", deleted_files)
    assert set(deleted_files) == set(expected)
    logger.info("Test passed!")

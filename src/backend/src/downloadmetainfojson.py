import abc
import pathlib
import extras
import downloadinfojson


class DownloadMetadataMissingError(Exception):
    def __init__(self, path: pathlib.Path):
        super().__init__(f"Missing download metadata file: {path}")
        self.path = path


class IDownloadInfoJsonGetter(abc.ABC):
    @abc.abstractmethod
    def get_json(
        self, path_to_download: pathlib.Path
    ) -> downloadinfojson.DownloadInfoJsonObj:
        pass


class DownloadInfoJsonGetter(IDownloadInfoJsonGetter):
    def get_json(
        self, path_to_download: pathlib.Path
    ) -> downloadinfojson.DownloadInfoJsonObj:
        json_path = extras.add_extension_to_path(path_to_download, ".json")
        if not json_path.exists():
            raise DownloadMetadataMissingError(json_path)
        json_str = json_path.read_text()
        json_obj = downloadinfojson.DownloadInfoJsonObj.model_validate_json(json_str)
        return json_obj


class MockDownloadInfoJsonGetter(IDownloadInfoJsonGetter):
    def __init__(self, given_json: downloadinfojson.DownloadInfoJsonObj) -> None:
        self.given_json = given_json

    def get_json(
        self, path_to_download: pathlib.Path
    ) -> downloadinfojson.DownloadInfoJsonObj:
        return self.given_json

import pathlib
import typing
import downloadstates
from fastapi_exceptions import DownloadIdMissingError
import pydantic


class DirectSerializedInfoFormat(pydantic.BaseModel):
    download_infos: typing.Mapping[str, downloadstates.DownloadStateVariants]


class DownloadInfoSerializerAndDeserializer:
    @staticmethod
    def deserialize_from_download_infos(
        given_infos: DirectSerializedInfoFormat,
    ) -> list[downloadstates.DownloadStateVariants]:
        return list(given_infos.download_infos.values())

    @staticmethod
    def deserialize_from_json(json_str: str):
        return DirectSerializedInfoFormat.model_validate_json(json_str)

    @staticmethod
    def deserialize_from_path(json_path: pathlib.Path):
        return DownloadInfoSerializerAndDeserializer.deserialize_from_json(
            json_path.read_text()
        )

    @staticmethod
    def serialize(to_serialize: DirectSerializedInfoFormat):
        return to_serialize

    @staticmethod
    def serialize_to_json(to_serialize: DirectSerializedInfoFormat):
        return to_serialize.model_dump_json()

    @staticmethod
    def serialize_to_path(
        to_serialize: DirectSerializedInfoFormat, json_path: pathlib.Path
    ):
        json_str = DownloadInfoSerializerAndDeserializer.serialize_to_json(to_serialize)
        json_path.write_text(json_str)

    @staticmethod
    def generate_dto_from_state_list(
        given_list: list[downloadstates.DownloadInfoState],
    ):
        required_format: dict[str, downloadstates.DownloadStateVariants] = {}
        for info in given_list:
            if info.download_id is None:
                raise DownloadIdMissingError()
            required_info_any: typing.Any = info
            required_info: downloadstates.DownloadStateVariants = required_info_any
            required_format[info.download_id] = required_info
        return DirectSerializedInfoFormat(download_infos=required_format)

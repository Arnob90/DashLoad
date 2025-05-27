from downloadstates import DownloadingInfo
import downloadinfoserializer


def test_serialization_and_deserialization():
    to_tests = [
        DownloadingInfo(
            download_id="test",
            downloaded_file_portion=50,
            filename="test",
            filepath="test",
            filesize=100,
            last_url="test",
            download_speed=10,
        )
    ]
    download_infos = {
        info.download_id: info for info in to_tests if info.download_id is not None
    }
    in_serialization_format = downloadinfoserializer.DirectSerializedInfoFormat(
        download_infos=download_infos
    )
    serialized = (
        downloadinfoserializer.DownloadInfoSerializerAndDeserializer.serialize_to_json(
            in_serialization_format
        )
    )
    deserialized = downloadinfoserializer.DownloadInfoSerializerAndDeserializer.deserialize_from_json(
        serialized
    )
    assert deserialized == in_serialization_format

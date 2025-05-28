import download_manager
from downloader import PypdlDownloader
import downloadinfoserializer
import downloaditem
import pathlib

import downloadstates


class DownloadManagerFactory:
    @staticmethod
    async def deserialize_from_json(json_str: str):
        deserialized_infos_dto = downloadinfoserializer.DownloadInfoSerializerAndDeserializer.deserialize_from_json(
            json_str
        )
        deserialized_infos = deserialized_infos_dto.download_infos
        required_manager = download_manager.DownloadManager()
        for id, info in deserialized_infos.items():
            if isinstance(info, downloadstates.FailedDownloadInfo) or isinstance(
                info, downloadstates.CancelledDownloadInfo
            ):
                required_manager.failed_or_cancelled_download_items[id] = info
                continue
            await required_manager.add_download_item(
                downloaditem.DownloadItem(
                    download_task=PypdlDownloader(
                        info.last_url, pathlib.Path(info.filepath)
                    ),
                    download_id=id,
                )
            )
        return required_manager

    @staticmethod
    async def serialize_to_json(
        download_manager: download_manager.DownloadManager,
    ) -> str:
        infos = await download_manager.get_all_download_infos()
        serialize_dto = downloadinfoserializer.DownloadInfoSerializerAndDeserializer.generate_dto_from_state_list(
            infos
        )
        serialized_json = serialize_dto.model_dump_json()
        return serialized_json

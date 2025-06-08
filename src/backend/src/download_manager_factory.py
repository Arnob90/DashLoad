import download_manager
import downloadinfoserializer
import pathlib
import logging
import downloadstates

main_logger = logging.getLogger(__name__)


class DownloadManagerFactory:
    @staticmethod
    async def deserialize_from_json(json_str: str):
        deserialized_infos_dto = downloadinfoserializer.DownloadInfoSerializerAndDeserializer.deserialize_from_json(
            json_str
        )
        # TODO: Remove debug statement
        # import debugpy
        #
        # debugpy.listen(("localhost", 5678))
        # main_logger.info("debugpy listening on 5678")
        # debugpy.wait_for_client()
        deserialized_infos = deserialized_infos_dto.download_infos
        required_manager = download_manager.DownloadManager()
        for id, info in deserialized_infos.items():
            if (
                isinstance(info, downloadstates.FailedDownloadInfo)
                or isinstance(info, downloadstates.CancelledDownloadInfo)
                or isinstance(info, downloadstates.PausedDownloadInfo)
            ):
                required_manager.terminal_download_items[id] = info
                continue

            await required_manager.add_pypdl_download(
                info.last_url, pathlib.Path(info.filepath), id
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

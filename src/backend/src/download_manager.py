import downloaditem
import asyncio
import downloadstates


class DownloadManager:
    def __init__(self):
        self.download_items: dict[str, downloaditem.DownloadItem] = {}

    def add_download_item(self, download_item: downloaditem.DownloadItem) -> str:
        self.download_items[download_item.download_id] = download_item

        def on_delete():
            del self.download_items[download_item.download_id]

        download_item.download_task.connect_delete_request_notify_callable(on_delete)

        return download_item.download_id

    def get_download_item(self, download_id: str) -> downloaditem.DownloadItem:
        return self.download_items[download_id]

    async def get_download_info_by_id(
        self, download_id: str
    ) -> downloadstates.DownloadInfoState:
        return await self.download_items[download_id].get_download_state()

    async def get_all_download_infos(self) -> list[downloadstates.DownloadInfoState]:
        download_state_futures = []
        for download_item in self.download_items.values():
            download_state_futures.append(download_item.get_download_state())
        return await asyncio.gather(*download_state_futures)

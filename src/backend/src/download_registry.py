import downloadinfos


class DownloadRegistry:
    def __init__(self) -> None:
        self.id_to_extra_infos: dict[str, downloadinfos.ExtraInfos] = {}

    def register(self, id: str, extra_infos: downloadinfos.ExtraInfos):
        self.id_to_extra_infos.update({id: extra_infos})

    def get(self, id: str) -> downloadinfos.ExtraInfos | None:
        return self.id_to_extra_infos.get(id)

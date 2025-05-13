from pydantic import BaseModel


class DownloadInfoJsonObj(BaseModel):
    url: str
    etag: str
    segments: int

import json
from attr import asdict
import fastapi
from pydantic import BaseModel
import download

app = fastapi.FastAPI()

download_manager = download.Downloader()


class DownloadRequest(BaseModel):
    url: str
    filepath: str


@app.get("/download/", response_model=list[download.DownloadInfo])
async def get_request():
    downloads_info = list(download_manager.query_downloads_info())
    return downloads_info


@app.post("/download/")
async def post_request(request: DownloadRequest):
    id = download_manager.download(request.url, request.filepath)
    return {"id": id}

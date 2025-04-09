import json
from attr import asdict
import fastapi
from pydantic import BaseModel
import pathlib
import download
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
download_manager = download.Downloader()


class DownloadRequest(BaseModel):
    url: str
    filepath: str


@app.get("/download/", response_model=list[download.DownloadInfo])
async def get_request():
    downloads_info = await download_manager.query_downloads_info()
    return downloads_info


@app.post("/download/")
async def post_request(request: DownloadRequest):
    id = await download_manager.download(request.url, pathlib.Path(request.filepath))
    return {"id": id}

import fastapi
from pydantic import BaseModel
import pathlib
import download
from fastapi.middleware.cors import CORSMiddleware
import extras
from typing import Union
import uvicorn

import logging


class SuppressSuccessfulGetFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Check for successful GETs: status 200 or 304
        return not ('"GET' in msg and (" 200" in msg or " 304" in msg or "207" in msg))


# Apply the filter to Uvicorn's access logger
access_logger = logging.getLogger("uvicorn.access")
access_logger.addFilter(SuppressSuccessfulGetFilter())

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


class DeleteRequest(BaseModel):
    delete_on_disk: bool


@app.get(
    "/download/",
    response_model=list[
        Union[
            download.DownloadingInfo,
            download.PausedDownloadInfo,
            download.FailedDownloadInfo,
            download.SucceededDownloadInfo,
        ]
    ],
)
async def get_request():
    downloads_info = await download_manager.query_downloads_info()
    return downloads_info


@app.post("/download/")
async def post_request(request: DownloadRequest) -> dict[str, str]:
    try:
        id = await download_manager.download(
            request.url, pathlib.Path(request.filepath)
        )
    except extras.InvalidDownloadUrlError:
        raise fastapi.HTTPException(status_code=404, detail="The given url is invalid")
    return {"id": id}


@app.get("/download/{id}", response_model=download.DownloadingInfo)
async def get_by_id(id: str):
    required_task = await download_manager.get_download_info_from_id(id)
    return required_task


@app.post("/download/pause/{id}")
async def pause_download(id: str):
    try:
        await download_manager.pause_download(id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail="The required download does not exist"
        )


@app.post("/download/stop/{id}")
async def stop_download(id: str):
    await download_manager.delete_download_task(id)


@app.post("/download/resume/{id}")
async def resume_download(id: str):
    await download_manager.resume_download(id)


@app.delete("/download/delete/{id}")
async def delete_download(id: str, request: DeleteRequest):
    await download_manager.delete_download_task(id, request.delete_on_disk)


@app.delete("/download/delete/{id}")
async def delete_download_default(id: str):
    await download_manager.delete_download_task(id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

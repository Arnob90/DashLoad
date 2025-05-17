import fastapi
from pydantic import BaseModel
import downloaditem
import download_manager
import downloadstates
import extras
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import uvicorn
import downloader
import pathlib


app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
dl_manager = download_manager.DownloadManager()


class DownloadRequest(BaseModel):
    url: str
    filepath: str


class DeleteRequest(BaseModel):
    delete_on_disk: bool


class DownloadStartResponse(BaseModel):
    id: str


DownloadStateVariants = list[
    Union[
        downloadstates.DownloadingInfo,
        downloadstates.PausedDownloadInfo,
        downloadstates.FailedDownloadInfo,
        downloadstates.SucceededDownloadInfo,
    ]
]


@app.get(
    "/download/",
    response_model=list[DownloadStateVariants],
)
async def get_request():
    downloads_info = await dl_manager.get_all_download_infos()
    return downloads_info


@app.post("/download/")
async def post_request(request: DownloadRequest) -> DownloadStartResponse:
    try:
        id = dl_manager.add_download_item(
            downloaditem.DownloadItem(
                downloader.PypdlDownloader(
                    request.url, pathlib.Path(request.filepath))
            )
        )
    except extras.InvalidDownloadUrlError:
        raise fastapi.HTTPException(
            status_code=404, detail="The given url is invalid")
    return DownloadStartResponse(id=id)


@app.get("/download/{id}", response_model=DownloadStateVariants)
async def get_by_id(id: str):
    required_task = await dl_manager.get_download_info_by_id(id)
    return required_task


@app.post("/download/pause/{id}")
async def pause_download(id: str):
    try:
        dl_manager.get_download_item(id).download_task.pause_download()
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail="The required download does not exist"
        )


@app.post("/download/stop/{id}")
async def stop_download(id: str):
    dl_manager.get_download_item(id).download_task.cancel_download()


@app.post("/download/resume/{id}")
async def resume_download(id: str):
    dl_manager.get_download_item(id).download_task.resume_download()


@app.post("/download/delete/{id}")
async def delete_download(id: str, request: DeleteRequest):
    delete_from_file = request.delete_on_disk
    dl_manager.get_download_item(id).download_task.delete_download_task(
        delete_from_file
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

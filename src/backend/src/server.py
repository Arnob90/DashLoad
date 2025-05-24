import fastapi
from pydantic import BaseModel
import downloaditem
import download_manager
import downloadstates
import extras
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Union
import uvicorn
import downloader
import pathlib
import argparse
import logging
import os
import json
from downloadstates import DownloadStateVariants

main_logger = logging.getLogger(__name__)
app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Add this
    allow_methods=["*"],
    allow_headers=["*"],
)


# The rationale is that, if a malicious process is able to execute the server directly, it can probably download
# through curl anyways, and so we have already lost
# This is mainly for testing purposes


class SecretHolderSingleton:
    _holder: extras.ISecretHolder = extras.FakeSecretHolder()

    @classmethod
    def set_holder(cls, holder: extras.ISecretHolder):
        cls._holder = holder

    @classmethod
    def verify_secret(cls, token: str) -> bool:
        return cls._holder.verify_secret(token)


dl_manager = download_manager.DownloadManager()


class DownloadRequest(BaseModel):
    url: str
    filepath: str


class DeleteRequest(BaseModel):
    delete_on_disk: bool


class DownloadStartResponse(BaseModel):
    id: str


class SerializeDownloadInfoRequest(BaseModel):
    filepath_to_serialize_to: str


class DeserializeDownloadInfoRequest(BaseModel):
    filepath_to_deserialize_from: str


DownloadStateVariants = Union[
    downloadstates.DownloadingInfo,
    downloadstates.PausedDownloadInfo,
    downloadstates.FailedDownloadInfo,
    downloadstates.SucceededDownloadInfo,
]


@app.get(
    "/download/",
    response_model=list[DownloadStateVariants],
)
async def get_request(x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    downloads_info = await dl_manager.get_all_download_infos()
    return downloads_info


@app.post("/download/")
async def post_request(
    request: DownloadRequest, x_session_token: Annotated[str, fastapi.Header()]
) -> DownloadStartResponse:
    assert SecretHolderSingleton.verify_secret(x_session_token)
    try:
        id = await dl_manager.add_download_item(
            downloaditem.DownloadItem(
                downloader.PypdlDownloader(request.url, pathlib.Path(request.filepath)),
            ),
        )
    except extras.InvalidDownloadUrlError:
        raise fastapi.HTTPException(status_code=404, detail="The given url is invalid")
    except extras.DownloadToAnExistingPathError as err:
        raise fastapi.HTTPException(status_code=409, detail=str(err))
    return DownloadStartResponse(id=id)


@app.get("/download/{id}", response_model=DownloadStateVariants)
async def get_by_id(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    try:
        required_task = await dl_manager.get_download_info_by_id(id)
    except KeyError:
        raise fastapi.HTTPException(
            status_code=404, detail="The required download does not exist"
        )
    return required_task


@app.post("/download/pause/{id}")
async def pause_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    try:
        dl_manager.get_download_item(id).download_task.pause_download()
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail="The required download does not exist"
        )


@app.post("/download/stop/{id}")
async def stop_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    await dl_manager.get_download_item(id).download_task.cancel_download()


@app.post("/download/resume/{id}")
async def resume_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    dl_manager.get_download_item(id).download_task.resume_download()


@app.post("/download/delete/{id}")
async def delete_download(
    id: str, request: DeleteRequest, x_session_token: Annotated[str, fastapi.Header()]
):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    delete_from_file = request.delete_on_disk
    logging.info(f"Delete request with local delete {delete_from_file}")
    await dl_manager.get_download_item(id).download_task.delete_download_task(
        delete_from_file
    )


@app.post("/download/serialize")
async def serialize_downloads(
    request: SerializeDownloadInfoRequest,
    x_session_token: Annotated[str, fastapi.Header()],
):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    serialized_infos = await dl_manager.serialize_download_infos()
    with open(request.filepath_to_serialize_to, "w") as f:
        json.dump(serialized_infos, f)


@app.post("/download/deserialize")
async def deserialize_downloads(
    request: DeserializeDownloadInfoRequest,
    x_session_token: Annotated[str, fastapi.Header()],
):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    with open(request.filepath_to_deserialize_from, "r") as f:
        serialized_infos = json.load(f)


@app.post("/shutdown")
async def shutdown(x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    os._exit(0)


logging.info("Logging is working")
if __name__ == "__main__":
    logging.info("Starting server")
    parser = argparse.ArgumentParser(
        prog="dashload-backend", description="Backend for the dashload download manager"
    )
    parser.add_argument("secret_key")
    parser.add_argument("serialize_downloads_path")
    args = parser.parse_args()
    secret_key = args.secret_key
    SecretHolderSingleton.set_holder(extras.SecretHolder(secret_key))
    dl_manager = download_manager.DownloadManager()
    uvicorn.run(app, host="0.0.0.0", port=8000)

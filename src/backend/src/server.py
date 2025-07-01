import asyncio
import download_manager_factory
import fastapi
from internet_connections import NetworkConnectionPoller
from pydantic import BaseModel
import download_manager
import extras
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import uvicorn
import pathlib
import argparse
import logging
from downloadstates import DownloadStateVariants
import fastapi_exceptions

main_logger = logging.getLogger(__name__)
app = fastapi.FastAPI()
server: uvicorn.Server | None = None
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


@app.exception_handler(fastapi_exceptions.ApiError)
async def handle_api_error(request: fastapi.Request, exc: fastapi_exceptions.ApiError):
    return await fastapi_exceptions.api_error_handler(request, exc)


class SecretHolderSingleton:
    _holder: extras.ISecretHolder = extras.FakeSecretHolder()

    @classmethod
    def set_holder(cls, holder: extras.ISecretHolder):
        cls._holder = holder

    @classmethod
    def verify_secret(cls, token: str) -> bool:
        return cls._holder.verify_secret(token)


dl_manager: download_manager.DownloadManager = download_manager.DownloadManager()


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


connection_tracker = NetworkConnectionPoller()


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


@app.get("/internet_available")
def check_internet_availablity():
    return connection_tracker.available


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
    id: str = ""
    id = await dl_manager.add_pypdl_download(
        request.url, pathlib.Path(request.filepath)
    )
    return DownloadStartResponse(id=id)


@app.get("/download/{id}", response_model=DownloadStateVariants)
async def get_by_id(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    try:
        required_task = await dl_manager.get_download_info_by_id(id)
    except KeyError:
        raise fastapi_exceptions.DownloadNotFoundError()
    return required_task


@app.post("/download/pause/{id}")
async def pause_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    try:
        dl_manager.pause_download(id)
    except ValueError:
        raise fastapi.HTTPException(
            status_code=404, detail="The required download does not exist"
        )


@app.post("/download/stop/{id}")
async def stop_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    await dl_manager.cancel_download(id)


@app.post("/download/resume/{id}")
async def resume_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    await dl_manager.resume_download(id)


@app.post("/download/delete/{id}")
async def delete_download(
    id: str, request: DeleteRequest, x_session_token: Annotated[str, fastapi.Header()]
):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    delete_from_file = request.delete_on_disk
    await dl_manager.delete_download_task(id, delete_from_file)


@app.post("/download/retry/{id}")
async def retry_download(id: str, x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    await dl_manager.retry_download(id)


@app.post("/download/serialize")
async def serialize_downloads(
    request: SerializeDownloadInfoRequest,
    x_session_token: Annotated[str, fastapi.Header()],
):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    json_str = await download_manager_factory.DownloadManagerFactory.serialize_to_json(
        dl_manager
    )
    json_path = pathlib.Path(request.filepath_to_serialize_to)
    json_path.write_text(json_str)


@app.post("/download/deserialize")
async def deserialize_downloads(
    request: DeserializeDownloadInfoRequest,
    x_session_token: Annotated[str, fastapi.Header()],
):
    if not SecretHolderSingleton.verify_secret(x_session_token):
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")
    json_path = pathlib.Path(request.filepath_to_deserialize_from)
    if not json_path.exists():
        # Nothing to serialize
        return
    json_str = json_path.read_text()
    required_manager = (
        await download_manager_factory.DownloadManagerFactory.deserialize_from_json(
            json_str
        )
    )
    global dl_manager
    dl_manager = required_manager


@app.post("/download/shutdown")
async def shutdown(x_session_token: Annotated[str, fastapi.Header()]):
    assert SecretHolderSingleton.verify_secret(x_session_token)
    main_logger.info("Shutting down from uvicorn")
    if server:
        await dl_manager.shutdown()
        server.should_exit = True
    else:
        raise fastapi.HTTPException(
            status_code=500, detail="The server is not running")


class ExtensionDownloadRequest(BaseModel):
    url: str


extension_download_request_queued: asyncio.Queue[ExtensionDownloadRequest] = (
    asyncio.Queue()
)


@app.post("/extension/download")
async def handle_extension_download_request(request: ExtensionDownloadRequest):
    await extension_download_request_queued.put(request)
    return


@app.websocket("/frontend/download/queue")
async def send_extension_download_request_to_client(websocket: fastapi.WebSocket):
    await websocket.accept()
    while True:
        request = await extension_download_request_queued.get()
        main_logger.info("Sending request to client")
        await websocket.send_json(request.model_dump())


logging.info("Logging is working")
if __name__ == "__main__":
    logging.info("Starting server")
    parser = argparse.ArgumentParser(
        prog="dashload-backend", description="Backend for the dashload download manager"
    )
    parser.add_argument("secret_key")
    args = parser.parse_args()
    secret_key = args.secret_key
    SecretHolderSingleton.set_holder(extras.SecretHolder(secret_key))
    dl_manager = download_manager.DownloadManager()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    server.run()

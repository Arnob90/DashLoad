import logging
from downloadstates import DownloadingInfo, PausedDownloadInfo
from fastapi.params import Path
from fastapi.testclient import TestClient
from server import DownloadRequest, app, DownloadStartResponse
import httpx
import pytest
from requests import Response
import time
import pathlib

main_logger = logging.getLogger(__name__)
client = TestClient(app, raise_server_exceptions=True)
main_logger.setLevel(logging.DEBUG)

path_to_test_downloads = pathlib.Path(__file__).parent.parent / "test_download_path"
headers = {"x-session-token": "fake key"}


def test_download_and_pause():
    logging.info(path_to_test_downloads)
    download_req = DownloadRequest(
        url="http://ipv4.download.thinkbroadband.com/1GB.zip",
        filepath=str(path_to_test_downloads),
    )
    response: httpx.Response = client.post(
        "/download/", json=download_req.model_dump(), headers=headers
    )
    assert response.status_code == 200
    response_json = response.json()
    res_body = DownloadStartResponse.model_validate(response_json)
    current_info = client.get(f"/download/{res_body.id}", headers=headers)
    current_info_json = current_info.json()
    main_logger.info(current_info_json)
    _ = DownloadingInfo.model_validate(current_info.json())
    res = client.post(f"/download/pause/{res_body.id}", headers=headers)
    paused_info = client.get(f"/download/{res_body.id}", headers=headers)
    paused_info_json = paused_info.json()
    main_logger.info(paused_info_json)
    _ = PausedDownloadInfo.model_validate(paused_info.json())
    main_logger.info(paused_info_json)
    client.post(
        f"/download/delete/{res_body.id}",
        json={"delete_on_disk": True},
        headers=headers,
    )
    res_after_delete = client.get(f"/download/{res_body.id}", headers=headers)
    main_logger.info(f"res_after_delete: {res_after_delete.json()}")
    assert res_after_delete.status_code == 404
    assert res.status_code == 200


def test_invalid_url():
    download_req = DownloadRequest(
        url="invalid url",
        filepath=str(path_to_test_downloads),
    )
    response: httpx.Response = client.post(
        "/download/", json=download_req.model_dump(), headers=headers
    )
    assert response.status_code == 404

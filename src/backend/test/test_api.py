from downloadstates import DownloadingInfo
from fastapi.testclient import TestClient
from server import DownloadRequest, app, DownloadStartResponse
import httpx
import pytest
from requests import Response
import time

client = TestClient(app)


@pytest.mark.integration
def test_download_and_pause():
    download_req = DownloadRequest(
        url="http://ipv4.download.thinkbroadband.com/1GB.zip",
        filepath="/tmp/",
    )
    response: httpx.Response = client.post(
        "/download/", json=download_req.model_dump())
    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    # Test schema
    res_body = DownloadStartResponse.model_validate(response.json())
    time.sleep(0.5)
    res = client.post(f"/download/pause/{res_body.id}")
    assert res.status_code == 200

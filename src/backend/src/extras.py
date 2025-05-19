import requests


def is_valid_download_url(url: str, timeout: float = 5.0) -> bool:
    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        # Some servers don't respond properly to HEAD, fall back to GET
        if response.status_code >= 400:
            response = requests.get(url, stream=True, timeout=timeout)

        content_type = response.headers.get("Content-Type", "")
        content_length = response.headers.get("Content-Length", None)

        # Basic check: content should not be HTML or empty
        if "text/html" in content_type.lower():
            return False
        if content_length is not None and int(content_length) == 0:
            return False

        return response.status_code == 200
    except requests.RequestException:
        return False

def supports_range(url:str):
    res = requests.head(url, allow_redirects=True)
    return res.headers.get("Accept-Ranges","") == "bytes"


class InvalidDownloadUrlError(Exception):
    def __init__(self, msg="The given download url is invalid") -> None:
        super().__init__(msg)

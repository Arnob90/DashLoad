import abc
import logging
import re
import urllib.parse
import os
import requests
import pathlib
import debugpy
import socket

main_logger = logging.getLogger(__name__)


def add_extension_to_path(path: pathlib.Path, extension: str):
    print(f"Adding {extension} to {path}")
    added_path = pathlib.Path(f"{path}{extension}")
    print(added_path)
    return added_path


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


def check_if_url_syntax_valid(url: str):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def internet_present(host: str = "8.8.8.8", port=53, timeout=3.0) -> bool:
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
        return True
    except socket.error:
        return False


def start_debug():
    print(f"PID: {os.getpid()}")
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.breakpoint()


class ISecretHolder(abc.ABC):
    @abc.abstractmethod
    def verify_secret(self, secret: str) -> bool:
        pass

    @abc.abstractmethod
    def throw_if_invalid(self, secret: str):
        pass


class SecretHolder(ISecretHolder):
    def __init__(self, secret: str) -> None:
        self.secret = secret

    def verify_secret(self, secret: str) -> bool:
        return self.secret == secret

    def throw_if_invalid(self, secret: str) -> None:
        if not self.verify_secret(secret):
            raise SecretMissingError()


class FakeSecretHolder(ISecretHolder):
    """A fake secret verifier for testing.
    If the server is started directly(that is: if __name__==__main__), SecretHolder will be used.
    Otherwise, this will used instead.
    The rationale is that, if a malicious process is able to execute the server directly, it can probably download
    through curl anyways, and so we have already lost
    This is mainly for testing purposes
    """

    def __init__(self) -> None:
        main_logger.info(
            "⚠️Using fake secret holder - secret verification is disabled!!!"
        )

    def verify_secret(self, secret: str) -> bool:
        return True

    def throw_if_invalid(self, secret: str) -> None:
        return


class InvalidDownloadUrlError(Exception):
    def __init__(self, msg="The given download url is invalid") -> None:
        super().__init__(msg)


class DownloadToAnExistingPathError(Exception):
    def __init__(self, msg="The given filepath already exists") -> None:
        super().__init__(msg)


class InvalidPathError(Exception):
    def __init__(self, msg="The given filepath is invalid") -> None:
        super().__init__(msg)


class SecretMissingError(Exception):
    def __init__(self, msg="The secret key wasn't passed in") -> None:
        super().__init__(msg)


class DownloadIdMissingError(Exception):
    def __init__(
        self,
        msg="The required download doesn't even have an id. \
        How is that possible?!",
    ) -> None:
        super().__init__(msg)


class InvalidUrl(Exception):
    def __init__(
        self,
        msg="The given url isn't syntatically valid",
    ) -> None:
        super().__init__(msg)

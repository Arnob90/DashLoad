import abc
import logging
import requests
import pathlib


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

import abc
from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse


class ApiErrorMeta(abc.ABCMeta):
    """Metaclass to ensure uniqueness of unique_error_strs and fail at import time if not unique"""

    def __new__(
        mcs: Any, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ):
        # isinstance won't work here, because this is at import time
        if abc.ABC in bases:
            # Thank God python creates classes in a parent-child order
            # Anyways, unique_error_strs is more of an implementation detail,
            # so why not put it in the metaclass?
            namespace.update({"unique_error_strs": set()}
                             )  # modify namespace first
        cls = super().__new__(mcs, name, bases, namespace)  # then create class
        if abc.ABC in bases:
            return cls  # then return if base
        unique_str: str | None = namespace.get("unique_error_str")
        if unique_str is None:
            raise ValueError(
                f"unique_error_str must be a class attribute! It is not present in class {
                    name
                }"
            )
        unique_error_strs: set[str] = cls.unique_error_strs
        if unique_str in unique_error_strs:
            raise TypeError(
                f"Error string {unique_str} is not unique! Class {
                    name
                } contains it too!"
            )
        cls.unique_error_strs.add(unique_str)
        return cls


class ApiError(abc.ABC, Exception, metaclass=ApiErrorMeta):
    """Any class that inherits from this class MUST have a unique_error_str namespace variable!!!!"""

    def __init__(
        self, detail: str, unique_error_str: str, status_code: int = 500
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.unique_error_str = unique_error_str

    # All abstract classes must have at least one abstract method. Otherwise, they can be init-ed
    # A python quirk
    @abc.abstractmethod
    def get_error(self):
        return {
            "detail": self.detail,
            "status_code": self.status_code,
            "content": {"type": self.unique_error_str},
        }


class InvalidDownloadUrlError(ApiError):
    unique_error_str = "invalid_download_url"

    def __init__(
        self,
        detail: str = "The given download url is invalid",
        status_code: int = 404,
    ) -> None:
        super().__init__(detail, self.unique_error_str, status_code)

    def get_error(self):
        return super().get_error()


class DownloadNotFoundError(ApiError):
    unique_error_str = "download_not_found"
    status_code = 404  # Not Found

    def __init__(
        self,
        detail: str = "The required download by id does not exist",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)

    def get_error(self):
        return super().get_error()


class InvalidUrl(ApiError):
    unique_error_str = "invalid_url"
    status_code = 400  # Bad Request

    def __init__(
        self,
        detail: str = "The given url isn't syntatically valid",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)


class InvalidPathError(ApiError):
    unique_error_str = "invalid_path"
    status_code = 400  # Bad Request

    def __init__(
        self,
        detail: str = "The given filepath is invalid",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)

    def get_error(self):
        return super().get_error()


class DownloadToAnExistingPathError(ApiError):
    unique_error_str = "download_to_existing_path"
    status_code = 409  # Conflict

    def __init__(
        self,
        detail: str = "The given filepath already exists",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)

    def get_error(self):
        return super().get_error()


class DownloadIdMissingError(ApiError):
    unique_error_str = "download_id_missing"
    status_code = 500  # Internal Server Error

    def __init__(
        self,
        detail: str = "The required download doesn't even have an id. How is that possible?!",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)

    def get_error(self):
        return super().get_error()


class SecretMissingError(ApiError):
    unique_error_str = "secret_missing"
    status_code = 401  # Unauthorized

    def __init__(
        self,
        detail: str = "The secret key wasn't passed in",
    ) -> None:
        super().__init__(detail, self.unique_error_str, self.status_code)

    def get_error(self):
        return super().get_error()


async def api_error_handler(_: Request, exc: ApiError):
    required_error = exc.get_error()
    status_code = required_error.get("status_code")
    if not isinstance(status_code, int):
        status_code = 500
    return JSONResponse(required_error, status_code=status_code)

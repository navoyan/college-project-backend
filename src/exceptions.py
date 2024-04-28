from typing import Any
from fastapi import HTTPException


class DetailedHTTPException(HTTPException):
    status_code: int
    detail: Any
    headers: dict[str, str] = {}

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=self.headers
        )

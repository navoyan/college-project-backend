from fastapi import status

from src.exceptions import DetailedHTTPException


class InvalidAccessToken(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate access token"
    headers = {"WWW-Authenticate": "Bearer"}

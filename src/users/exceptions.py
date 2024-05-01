from starlette import status

from src.exceptions import DetailedHTTPException


class IncorrectCredentials(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect username or password"
    headers = {"WWW-Authenticate": "Bearer"}


class EmailAlreadyExists(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email already exists"


class InvalidOrExpiredValidationToken(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid or expired validation token"


class InsufficientUserRights(DetailedHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "This operation is forbidden for this resource"


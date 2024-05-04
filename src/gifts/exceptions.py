from fastapi import status
from src.exceptions import DetailedHTTPException


class GiftNotFound(DetailedHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Quiz not found"


class GiftAlreadyReceived(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Gift has already been received"


class NotEnoughPoints(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "User does not have enough points to verify receipt"

from fastapi import status
from src.exceptions import DetailedHTTPException


class QuizNotFound(DetailedHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Quiz not found"


class QuizAlreadyCompleted(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Quiz is already completed"


from fastapi import HTTPException, status


class PhoneNumberAlreadyExists(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = "Phone number already exists"


class UserNotFound(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "There is no active account with the provided info!"


class CredentialsException(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        self.headers = {"WWW-Authenticate": "Bearer"}


class IsAdminException(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "Only admin users can access to this endpoint!"


class InvalidVerificationCode(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Verification code is invalid, get a new one!"


class InvalidRandomPassword(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Random Password is invalid, get a new one!"


class NotActiveUser(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "This account is not active!"


class WrongOldPassword(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Old password is wrong!"

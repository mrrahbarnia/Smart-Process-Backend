import re

from typing import Annotated, Self
from pydantic import (
    BaseModel, ConfigDict, model_validator, Field, field_validator
)

from src.schemas import CustomBaseModel
from src.auth.config import auth_config
from src.auth.types import Password, PhoneNumber

PASSWORD_PATTERN = auth_config.PASSWORD_PATTERN


class RegisterOut(CustomBaseModel):
    phone_number: Annotated[PhoneNumber, Field(alias="phoneNumber")]


class RegisterIn(RegisterOut):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "phoneNumber": "09131111111",
                "password": "12345678",
                "confirmPassword": "12345678",
            }
        ]
    })
    password: Password
    confirm_password: Annotated[Password, Field(alias="confirmPassword")]

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        password = self.password
        confirm_password = self.confirm_password

        if password is not None and confirm_password is not None and password != confirm_password:
            raise ValueError("Passwords don't match!")
        return self

    @field_validator("phone_number", mode="after")
    @classmethod
    def validate_phone_length(cls, phone_number: PhoneNumber) -> PhoneNumber:
        if phone_number and len(phone_number) != 11:
            raise ValueError("Phone number must has exact 11 length!")
        return phone_number

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: Password) -> Password:
        if not re.match(PASSWORD_PATTERN, value):
            raise ValueError(
                "Password must contain at least 8 chars!"
            )
        return value


class LoginIn(BaseModel):
    username: PhoneNumber
    password: Password


class LoginOut(BaseModel):
    username: str
    access_token: str
    token_type: str


class VerificationIn(CustomBaseModel):
    verification_code: str = Field(alias="verificationCode")

    @field_validator("verification_code", mode="after")
    @classmethod
    def validate_length(cls, value: str) -> str:
        if value and len(value) != 6:
            raise ValueError("Verification code must be always 6 chars!")
        return value


class ResendVerificationCode(BaseModel):
    phone_number: Annotated[PhoneNumber, Field(alias="phoneNumber")]

    @field_validator("phone_number", mode="after")
    @classmethod
    def validate_verification_code(cls, phone_number: PhoneNumber) -> PhoneNumber:
        if phone_number and len(phone_number) != 11:
            raise ValueError("Phone number must has exact 11 length!")
        return phone_number


class ChangePasswordIn(CustomBaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {   
                "oldPassword": "12345678",
                "newPassword": "12345678",
                "confirmPassword": "12345678",
            }
        ]
    })
    old_password: Password = Field(alias="oldPassword")
    new_password: Password = Field(alias="newPassword")
    confirm_password: Password = Field(alias="confirmPassword")

    @field_validator("new_password", mode="after")
    @classmethod
    def validate_password_pattern(cls, new_password: Password) -> Password:
        if not re.match(PASSWORD_PATTERN, new_password):
            raise ValueError(
                "Password must has minimum 8 characters."
            )
        return new_password

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        new_password = self.new_password
        confirm_password = self.confirm_password
        if new_password is not None and confirm_password is not None and new_password != confirm_password:
            raise ValueError("Passwords don't match!")
        return self


class ResetPasswordIn(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "phoneNumber": "09131111111"
            }
        ]
    })
    phone_number: Annotated[PhoneNumber, Field(alias="phoneNumber")]

    @field_validator("phone_number", mode="after")
    @classmethod
    def validate_phone_length(cls, phone_number: PhoneNumber) -> PhoneNumber:
        if phone_number and len(phone_number) != 11:
            raise ValueError("Phone number must has exact 11 numbers!")
        return phone_number


class VerifyResetPasswordIn(CustomBaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "randomPassword": "12345678"
            }
        ]
    })
    random_password: Annotated[Password, Field(alias="randomPassword")]

    @field_validator("random_password", mode="after")
    @classmethod
    def validate_password_length(cls, random_password: Password) -> Password:
        if random_password and len(random_password) != 8:
            raise ValueError("Random password must has exact 8 chars!")
        return random_password

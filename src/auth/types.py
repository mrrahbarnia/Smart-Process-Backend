from typing import NewType
from enum import Enum

class UserRule(Enum):
    USER = "user"
    ADMIN = "admin"

UserId = NewType("UserId", int)
PhoneNumber = NewType("PhoneNumber", str)
Password = NewType("Password", str)
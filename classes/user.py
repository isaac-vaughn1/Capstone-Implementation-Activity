# need to import Reservation class when it is made.
from __future__ import annotations
import hashlib
from datetime import datetime, timedelta

class User:
    _nextUserId = 1
    _maxLoginAttempts = 5
    _lockoutMinutes = 15

    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        self._userId = userId
        self._name = name
        self._email = email
        self._passwordHash = passwordHash
        self._isActive = False
        self._failedLoginAttempts = 0
        self._lockedUntil = None
        self._reservations = []

    @staticmethod
    def _hashPassword(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def register(cls, name: str, email: str, password: str) -> User:
        user = cls(User._nextUserId, name, email, User._hashPassword(password))
        User._nextUserId += 1
        return user

    def login(self, email: str, password: str) -> bool:
        if self._lockedUntil is not None and datetime.now() < self._lockedUntil:
            return False
        if self._email == email and self._passwordHash == User._hashPassword(password):
            self._isActive = True
            self._failedLoginAttempts = 0
            self._lockedUntil = None
            return True
        self._failedLoginAttempts += 1
        if self._failedLoginAttempts >= User._maxLoginAttempts:
            self._lockedUntil = datetime.now() + timedelta(minutes=User._lockoutMinutes)
            self._failedLoginAttempts = 0
        return False

    def logout(self):
        self._isActive = False

    def getMyReservations(self) -> list[Reservation]:
        return list(self._reservations)

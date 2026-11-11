# need to import Event and Reservation classes when they are made.
from __future__ import annotations
from user import User

class Student(User):
    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        super().__init__(userId, name, email, passwordHash)

    def scheduleEvent(self, event: Event) -> Reservation:
        # need to create the Reservation once the Reservation class is made.
        reservation = None
        self._reservations.append(reservation)
        return reservation

    def editEvent(self, event: Event):
        # need to call event.updateDetails() once the Event class is made.
        pass

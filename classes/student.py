# need to import Event class when it is made.
from __future__ import annotations
from datetime import datetime
from user import User
from reservation import Reservation
from RoomFacilityClasses import room as Room

class Student(User):
    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        super().__init__(userId, name, email, passwordHash)

    def scheduleEvent(self, event: Event, room: Room, start_time: datetime, end_time: datetime,
                      equipment_needed=None, support_needed=None) -> Reservation:
        # creates a draft reservation; call reservation.submit() to send it for approval
        reservation = Reservation(self, event, room, start_time, end_time,
                                  equipment_needed, support_needed)
        self._reservations.append(reservation)
        return reservation

    def editEvent(self, event: Event):
        # need to call event.updateDetails() once the Event class is made.
        pass

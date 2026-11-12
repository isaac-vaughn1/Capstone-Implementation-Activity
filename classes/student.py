from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from user import User
from reservation import Reservation

if TYPE_CHECKING:
    from RoomFacilityClasses import room as Room
    from event import Event

class Student(User):
    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        super().__init__(userId, name, email, passwordHash)

    def scheduleEvent(self, event: Event, room: Room, start_time: datetime, end_time: datetime,
                      equipment_needed=None, support_needed=None) -> Reservation:
        # creates a draft reservation; call reservation.submit() to send it for approval
        reservation = Reservation(self, event, room, start_time, end_time,
                                  equipment_needed, support_needed)
        self._reservations.append(reservation)
        room.reservations.append(reservation)  # lets room.isAvailable()/getSchedule() see it
        return reservation

    def editEvent(self, event: Event, title: str = None, description: str = None) -> Event:
        # students can only edit events they scheduled; fields left as None keep their current value
        if not any(r.event is event for r in self._reservations):
            raise PermissionError("Students can only edit events they scheduled")
        event.updateDetails(title if title is not None else event.title,
                            description if description is not None else event.description)
        return event

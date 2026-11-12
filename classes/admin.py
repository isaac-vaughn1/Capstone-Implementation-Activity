# need to import Event class when it is made.
from __future__ import annotations
from typing import TYPE_CHECKING
from user import User

if TYPE_CHECKING:
    from RoomFacilityClasses import facility as Facility, room as Room

class Admin(User):
    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        super().__init__(userId, name, email, passwordHash)

    def editEvent(self, event: Event):
        # need to call event.updateDetails() once the Event class is made.
        pass

    def editFacility(self, facility: Facility, name: str = None, location: str = None,
                     facilityType: str = None, isActive: bool = None) -> Facility:
        if name is not None:
            facility.name = name
        if location is not None:
            facility.location = location
        if facilityType is not None:
            facility.facilityType = facilityType
        if isActive is not None:
            facility.isActive = isActive
        return facility

    def editRoom(self, room: Room, roomNumber=None, capacity: int = None, features=None) -> Room:
        if capacity is not None and capacity <= 0:
            raise ValueError("Room capacity must be greater than 0")
        if roomNumber is not None:
            room.roomNumber = roomNumber
        if capacity is not None:
            room.capacity = capacity
        if features is not None:
            room.features = list(features)
        return room

    def addAdmin(self, user: User):
        if not isinstance(user, Admin):
            user.__class__ = Admin

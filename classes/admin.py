# need to import Event, Facility, and Room classes when they are made.
from __future__ import annotations
from user import User

class Admin(User):
    def __init__(self, userId: int, name: str, email: str, passwordHash: str):
        super().__init__(userId, name, email, passwordHash)

    def editEvent(self, event: Event):
        # need to call event.updateDetails() once the Event class is made.
        pass

    def editFacility(self, facility: Facility):
        # need to update the facility once the Facility class is made.
        pass

    def editRoom(self, room: Room):
        # need to update the room once the Room class is made.
        pass

    def addAdmin(self, user: User):
        if not isinstance(user, Admin):
            user.__class__ = Admin

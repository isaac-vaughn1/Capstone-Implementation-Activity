from reservation import Reservation
from datetime import datetime

class Event:
    def __init__(self, eventId: int, title: str, description: str, expectedAttendance: int, isPublic: bool):
        self.eventId = eventId
        self.title = title
        self.description = description
        self.expectedAttendance = expectedAttendance
        self.isPublic = isPublic

    def updateDetails(self, title: str, description: str):
        self.title = title
        self.description = description

    def is_Upcoming(self, reservation):
        if reservation.event.eventId == self.eventId and reservation.start_time > datetime.now():
            return True
        return False

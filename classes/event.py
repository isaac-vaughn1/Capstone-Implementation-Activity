from reservation import reservation
from datetime import datetime

class user:
    def __init__(self, eventId: int, title: str, description: str, expectedAttendance: int, isPublic: bool):
        self.eventId = eventId
        self.title = title
        self.description = description
        self.expectedAttendance = expectedAttendance
        self.isPublic = isPublic

    def __updateDetails__(self, title: str, description: str):
        self.title = title
        self.description = description

    def __is__Upcoming__(self):
        if reservation.eventId == self.eventId and reservation.startTime > datetime.now():
            return True
        return False